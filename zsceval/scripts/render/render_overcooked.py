#!/usr/bin/env python
import os
import socket
import sys
from pathlib import Path

import setproctitle
import torch
import wandb

from zsceval.config import get_config
from zsceval.envs.env_wrappers import ShareDummyVecEnv, ShareSubprocDummyBatchVecEnv
from zsceval.envs.overcooked.Overcooked_Env import Overcooked
from zsceval.envs.overcooked_new.Overcooked_Env import Overcooked as Overcooked_new
from zsceval.overcooked_config import get_overcooked_args
from zsceval.utils.train_util import get_base_run_dir, setup_seed


def make_render_env(all_args, run_dir):
    def get_env_fn(rank):
        def init_env():
            if all_args.env_name == "Overcooked":
                if all_args.overcooked_version == "old":
                    env = Overcooked(all_args, run_dir, evaluation=True)
                else:
                    env = Overcooked_new(all_args, run_dir, evaluation=True)
            else:
                print("Can not support the " + all_args.env_name + "environment.")
                raise NotImplementedError
            env.seed(all_args.seed * 50000 + rank * 10000)
            return env

        return init_env

    if all_args.n_eval_rollout_threads == 1:
        return ShareDummyVecEnv([get_env_fn(0)])
    else:
        return ShareSubprocDummyBatchVecEnv(
            [get_env_fn(i) for i in range(all_args.n_rollout_threads)],
            all_args.dummy_batch_size,
        )


def parse_args(args, parser):
    parser = get_overcooked_args(parser)
    parser.add_argument(
        "--use_phi",
        default=False,
        action="store_true",
        help="While existing other agent like planning or human model, use an index to fix the main RL-policy agent.",
    )

    parser.add_argument("--use_task_v_out", default=False, action="store_true")
    # all_args = parser.parse_known_args(args)[0]
    all_args = parser.parse_args(args)
    from zsceval.overcooked_config import OLD_LAYOUTS

    if all_args.layout_name in OLD_LAYOUTS:
        all_args.old_dynamics = True
    else:
        all_args.old_dynamics = False
    return all_args


def main(args):
    parser = get_config()
    all_args = parse_args(args, parser)

    if all_args.algorithm_name == "rmappo" or all_args.algorithm_name == "rmappg":
        assert all_args.use_recurrent_policy or all_args.use_naive_recurrent_policy, "check recurrent policy!"
    elif all_args.algorithm_name == "mappo" or all_args.algorithm_name == "mappg":
        assert (
            all_args.use_recurrent_policy == False and all_args.use_naive_recurrent_policy == False
        ), "check recurrent policy!"
    else:
        raise NotImplementedError

    # cuda
    if all_args.cuda and torch.cuda.is_available():
        print("choose to use gpu...")
        device = torch.device("cuda:0")
        torch.set_num_threads(all_args.n_training_threads)
        if all_args.cuda_deterministic:
            torch.backends.cudnn.benchmark = False
            torch.backends.cudnn.deterministic = True
    else:
        print("choose to use cpu...")
        device = torch.device("cpu")
        torch.set_num_threads(all_args.n_training_threads)

    base_run_dir = Path(get_base_run_dir())
    run_dir = (
        base_run_dir / all_args.env_name / all_args.layout_name / all_args.algorithm_name / all_args.experiment_name
    )
    if not run_dir.exists():
        os.makedirs(str(run_dir))
    all_args.run_dir = run_dir

    # wandb
    if all_args.overcooked_version == "new":
        project_name = all_args.env_name + "-new"
    else:
        project_name = all_args.env_name
    if all_args.use_wandb:
        run = wandb.init(
            config=all_args,
            project=project_name,
            entity=all_args.wandb_name,
            notes=socket.gethostname(),
            name=str(all_args.algorithm_name) + "_" + str(all_args.experiment_name) + "_seed" + str(all_args.seed),
            group=all_args.layout_name,
            dir=str(run_dir),
            job_type="training",
            reinit=True,
            tags=all_args.wandb_tags,
        )
    else:
        if not run_dir.exists():
            curr_run = "run1"
        else:
            exst_run_nums = [
                int(str(folder.name).split("run")[1])
                for folder in run_dir.iterdir()
                if str(folder.name).startswith("run")
            ]
            if len(exst_run_nums) == 0:
                curr_run = "run1"
            else:
                curr_run = "run%i" % (max(exst_run_nums) + 1)
        run_dir = run_dir / curr_run
        if not run_dir.exists():
            os.makedirs(str(run_dir))

    setproctitle.setproctitle(
        str(all_args.algorithm_name)
        + "-"
        + str(all_args.env_name)
        + "_"
        + str(all_args.layout_name)
        + "-"
        + str(all_args.experiment_name)
        + "@"
        + str(all_args.user_name)
    )

    # seed
    # torch.manual_seed(all_args.seed)
    # torch.cuda.manual_seed_all(all_args.seed)
    # np.random.seed(all_args.seed)
    setup_seed(all_args.seed)
    # env init
    envs = make_render_env(all_args, run_dir)
    num_agents = all_args.num_agents

    config = {
        "all_args": all_args,
        "envs": envs,
        "eval_envs": None,
        "num_agents": num_agents,
        "device": device,
        "run_dir": run_dir,
    }

    # run experiments
    from zsceval.runner.shared.overcooked_runner import OvercookedRunner as Runner

    runner = Runner(config)
    runner.render()

    # post process
    envs.close()


if __name__ == "__main__":
    main(sys.argv[1:])
