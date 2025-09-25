import torch
from module.decoder.models import gvmgen

CKPT_PATHS = [
    #"/app/code/checkpoints/state_dict.bin",
    "/app/code/checkpoints_tunado/state_dict.bin"
]

def main():
    #for ckpt_path in CKPT_PATHS:
    # state_dict = torch.load(ckpt_path)
    # print(state_dict['best_state'].keys())

    model = gvmgen.GVMGen.get_pretrained("/app/code/checkpoints_tunado", device='cuda')
    print(model.lm)

if __name__ == "__main__":
    main()