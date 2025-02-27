from PIL import Image
import torch
from tqdm.auto import tqdm
import argparse

from point_e.diffusion.configs import DIFFUSION_CONFIGS, diffusion_from_config
from point_e.diffusion.sampler import PointCloudSampler
from point_e.models.download import load_checkpoint
from point_e.models.configs import MODEL_CONFIGS, model_from_config
from point_e.util.plotting import plot_point_cloud
from point_e.util.pc_to_mesh import marching_cubes_mesh
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

def parse(raw_args=None):
    p = argparse.ArgumentParser()
    p.add_argument('--input_file', type=str, default='input/image.png', help='Input image file path. RGB, png.')
    p.add_argument('--output_pcd', type=str, default='output/pcd.ply', help='Output point cloud file path.')
    p.add_argument('--save_mesh', action='store_true', help='Save mesh along with point cloud')
    p.add_argument('--output_mesh', type=str, default='output/mesh.ply', help='Output mesh file path.')
    return p.parse_args(raw_args)


def main(raw_args=None):
    args = parse(raw_args)
    
    print('creating base model...')
    base_name = 'base40M' # use base300M or base1B for better results
    base_model = model_from_config(MODEL_CONFIGS[base_name], device)
    base_model.eval()
    base_diffusion = diffusion_from_config(DIFFUSION_CONFIGS[base_name])

    print('creating upsample model...')
    upsampler_model = model_from_config(MODEL_CONFIGS['upsample'], device)
    upsampler_model.eval()
    upsampler_diffusion = diffusion_from_config(DIFFUSION_CONFIGS['upsample'])

    print('downloading base checkpoint...')
    base_model.load_state_dict(load_checkpoint(base_name, device))

    print('downloading upsampler checkpoint...')
    upsampler_model.load_state_dict(load_checkpoint('upsample', device))
    sampler = PointCloudSampler(
        device=device,
        models=[base_model, upsampler_model],
        diffusions=[base_diffusion, upsampler_diffusion],
        num_points=[1024, 4096 - 1024],
        aux_channels=['R', 'G', 'B'],
        guidance_scale=[3.0, 3.0],
    )
    # Load an image to condition on.
    img = Image.open(args.input_file)

    # Produce a sample from the model.
    samples = None
    for x in tqdm(sampler.sample_batch_progressive(batch_size=1, model_kwargs=dict(images=[img]))):
        samples = x
    pc = sampler.output_to_point_clouds(samples)[0]
    with open(args.output_pcd, "wb") as f:
        pc.write_ply(f)

    if args.save_mesh:
        print('creating SDF model...')
        name = 'sdf'
        sdf_model = model_from_config(MODEL_CONFIGS[name], device)
        sdf_model.eval()

        print('loading SDF model...')
        sdf_model.load_state_dict(load_checkpoint(name, device))

        mesh = marching_cubes_mesh(
                pc=pc,
                model=sdf_model,
                batch_size=4096,
                grid_size=256, # increase to 128 for resolution used in evals
                progress=True,
        )

        # Write the mesh to a PLY file to import into some other program.
        with open(args.output_mesh, 'wb') as f:
            mesh.write_ply(f)

if __name__ == "__main__":
    main()