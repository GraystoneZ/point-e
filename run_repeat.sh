#!bin/bash

DIRNAMES=("obj_hedgehog_2" "obj_shoe_2" "obj_lion_statue_1" "obj_buddha_1" "obj_robot_1" "obj_berry_2" "obj_cactus_2" "obj_broccoli_2" "obj_pear_2" "obj_cat_1" "obj_camera_bag_2" "obj_doll_statue_2" "obj_fire_hydrant_2" "obj_flower_2" "obj_gingerbread_man_2" "obj_frog_1" "obj_croissant_1" "obj_mushroom_2" "obj_extinguisher_1" "obj_owl_1")

for i in {0..19}
do
    bash run.sh 3 ${DIRNAMES[i]} no
done