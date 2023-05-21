#!bin/bash

GPU_ID=$1
DIRNAME=$2
SAVE_MESH=$3

mkdir -p preprocess/$DIRNAME
mkdir -p output/$DIRNAME
set -e
exec > >(tee "output/$DIRNAME/output.log") 2>&1

echo "Running Point-E"
echo "GPU_ID=$1, DIRNAME=$2, SAVE_MESH=$3"

START=`date +%s`

INPUT_FILES=("./input/$DIRNAME"/*)

if [ ${#INPUT_FILES[@]} -ne 1 ]; then
    echo "Error : There should be only one image file in input directory."
    exit
fi

ORG_INPUT_FILE=$(basename -- "${INPUT_FILES[0]}")

# If file name contains ".", following step doesn't work. So rename image file.
cp input/$DIRNAME/$ORG_INPUT_FILE input/$DIRNAME/image.png
INPUT_FILE="image.png"
INPUT_NO_EXT=$(basename $INPUT_FILE ".png")

mkdir -p tmp/$DIRNAME
mv input/$DIRNAME/$ORG_INPUT_FILE tmp/$DIRNAME/$ORG_INPUT_FILE

python rgba_to_rgb_mask.py --input_file input/$DIRNAME/$INPUT_FILE --output_dir preprocess/$DIRNAME

mv tmp/$DIRNAME/$ORG_INPUT_FILE input/$DIRNAME/$ORG_INPUT_FILE
rm -f input/$DIRNAME/image.png

if [ "$SAVE_MESH" == "yes" ]; then
    CUDA_VISIBLE_DEVICES=$GPU_ID python main.py --input_file preprocess/$DIRNAME/image.png \
                                                --output_pcd output/$DIRNAME/pcd.ply
else
    CUDA_VISIBLE_DEVICES=$GPU_ID python main.py --input_file preprocess/$DIRNAME/image.png \
                                                --output_pcd output/$DIRNAME/pcd.ply \
                                                --save_mesh \
                                                --output_mesh output/$DIRNAME/mesh.ply
fi


END=`date +%s`
RUNTIME=$((END - START))
HOURS=$((RUNTIME / 3600))
MINUTES=$(( (RUNTIME % 3600) / 60 ))
SECONDS=$(( (RUNTIME % 3600) % 60 ))
echo "Runtime $HOURS:$MINUTES:$SECONDS (hh:mm:ss)"