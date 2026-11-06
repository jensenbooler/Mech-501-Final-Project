#!/bin/bash
set -e

AIRFOIL="0012"
mkdir -p data

for LVL in h3 h2 h1; do
    echo "=========================================="
    echo " Generating & Converting Mesh: ${LVL}"
    echo "=========================================="

    CASE_DIR="setup/naca${AIRFOIL}/${LVL}"
    GEO_FILE="naca_${AIRFOIL}_${LVL}.geo"
    MSH_FILE="data/naca_${AIRFOIL}_${LVL}.msh"

    # 1. Generate Gmsh .geo and compile to .msh
    python3 scripts/generate_mesh.py ${LVL} ${AIRFOIL}
    gmsh -3 -format msh2 ${GEO_FILE} -o ${MSH_FILE}
    rm -f ${GEO_FILE}

    # 2. Set up case directories and minimal controlDict
    mkdir -p ${CASE_DIR}/system ${CASE_DIR}/constant
    cat << 'EOF' > ${CASE_DIR}/system/controlDict
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    location    "system";
    object      controlDict;
}

application     simpleFoam;
startFrom       startTime;
startTime       0;
stopAt          endTime;
endTime         1000;
deltaT          1;
writeControl    timeStep;
writeInterval   100;
purgeWrite      0;
writeFormat     ascii;
writePrecision  6;
writeCompression off;
timeFormat      general;
timePrecision   6;
runTimeModifiable true;
EOF

    # 3. Convert Gmsh mesh to OpenFOAM
    gmshToFoam ${MSH_FILE} -case ${CASE_DIR}

    # 4. Set 2D planar patch to empty
    sed -i '/frontAndBack/,/}/ s/type.*patch;/type empty;/' ${CASE_DIR}/constant/polyMesh/boundary

    # 5. Run checkMesh and filter key quality metrics
    echo "--- checkMesh summary for ${LVL} ---"
    checkMesh -case ${CASE_DIR} | grep -E "(cells:|Mesh non-orthogonality Max:|Mesh OK\.)"
    echo ""
done

echo "All 3 meshes generated, converted, and verified."