#!/usr/bin/env python3
import argparse
import logging
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import uuid


def get_parser():
    parser = argparse.ArgumentParser(
        description="Launch distributed process with appropriate options. ",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--expname",
        help="hydra.run.dir will be ./exp/expname",
    )
    parser.add_argument(
        "--log",
        help="The path of log file used by cmd",
        default="run.log",
    )
    parser.add_argument(
        "--max_num_log_files",
        help="The maximum number of log-files to be kept",
        default=1000,
    )
    parser.add_argument(
        "--ngpu", type=int, default=1, help="The number of GPUs per node"
    )
    parser.add_argument(
        "--host",
        type=str,
        default=None,
        help="Directly specify the host names.  The job are submitted via SSH. "
        "Multiple host names can be specified by splitting by comma. e.g. host1,host2"
        " You can also the device id after the host name with ':'. e.g. "
        "host1:0:2:3,host2:0:2. If the device ids are specified in this way, "
        "the value of --ngpu is ignored.",
    )
    parser.add_argument(
        "--envfile",
        type=str,
        default="path.sh",
        help="Source the shell script before executing command. "
        "This option is used when --host is specified.",
    )
    parser.add_argument(
        "--master_port",
        type=int,
        default=None,
        help="Specify the port number of master"
        "Master is a host machine has RANK0 process.",
    )
    parser.add_argument(
        "--master_addr",
        type=str,
        default=None,
        help="Specify the address s of master. "
        "Master is a host machine has RANK0 process.",
    )
    parser.add_argument("args", type=str, nargs="+")
    return parser


def get_commandline_args():
    extra_chars = [
        " ",
        ";",
        "&",
        "(",
        ")",
        "|",
        "^",
        "<",
        ">",
        "?",
        "*",
        "[",
        "]",
        "$",
        "`",
        '"',
        "\\",
        "!",
        "{",
        "}",
    ]

    # Escape the extra characters for shell
    argv = [
        arg.replace("'", "'\\''")
        if all(char not in arg for char in extra_chars)
        else "'" + arg.replace("'", "'\\''") + "'"
        for arg in sys.argv
    ]

    return sys.executable + " " + " ".join(argv)


def main(cmd=None):
    logfmt = "%(asctime)s (%(module)s:%(lineno)d) %(levelname)s: %(message)s"
    logging.basicConfig(level=logging.INFO, format=logfmt)
    logging.info(get_commandline_args())

    parser = get_parser()
    args = parser.parse_args(cmd)

    rundir = Path("./exp").absolute() / Path(args.expname)

    if args.log != "-":
        logfile = rundir / Path(args.log)
        # Log-rotation
        for i in range(args.max_num_log_files - 1, -1, -1):
            if i == 0:
                p = logfile
                pn = p.parent / (p.stem + ".1" + p.suffix)
            else:
                _p = logfile
                p = _p.parent / (_p.stem + f".{i}" + _p.suffix)
                pn = _p.parent / (_p.stem + f".{i + 1}" + _p.suffix)

            if p.exists():
                if i == args.max_num_log_files - 1:
                    p.unlink()
                else:
                    shutil.move(p, pn)

    processes = []
    # Submit command via SSH
    if args.host is not None:
        hosts = []
        ids_list = []
        # e.g. args.host = "host1:0:2,host2:0:1"
        for host in args.host.split(","):
            # e.g host = "host1:0:2"
            sps = host.split(":")
            host = sps[0]
            if len(sps) > 1:
                ids = [int(x) for x in sps[1:]]
            else:
                ids = list(range(args.ngpu))
            hosts.append(host)
            ids_list.append(ids)

        world_size = sum(max(len(x), 1) for x in ids_list)
        logging.info(f"{len(hosts)}nodes with world_size={world_size} via SSH")

        if args.envfile is not None:
            env = f"source {args.envfile}"
        else:
            env = ""

        if args.log != "-":
            logfile.parent.mkdir(parents=True, exist_ok=True)
            f = logfile.open("w", encoding="utf-8")
        else:
            # Output to stdout/stderr
            f = None

        rank = 0
        logging.info(f"env={env}")
        logging.info(f"hosts={hosts}, ids_list={ids_list}")
        for host, ids in zip(hosts, ids_list):
            cmd = args.args + [
                f"distributed_training.distributed_init_method=tcp://{hosts[0]}:{args.master_port}",
                f"distributed_training.distributed_rank={rank}",
                f"distributed_training.distributed_world_size={world_size}",
                f"hydra.run.dir={str(rundir)}",
            ]

            heredoc = f"""<< EOF
set -euo pipefail
cd {os.getcwd()}
{env}
{" ".join([c if len(c) != 0 else "''" for c in cmd])}
EOF
"""

            logging.info(" ".join(["ssh", host, "bash", heredoc]))
            print(" ".join(["ssh", host, "bash", heredoc]), file=f, flush=True)
            # FIXME(kamo): The process will be alive
            #  even if this program is stopped because we don't set -t here,
            #  i.e. not assigning pty,
            #  and the program is not killed when SSH connection is closed.
            process = subprocess.Popen(
                ["ssh", host, "bash", heredoc],
                stdout=f,
                stderr=f,
            )

            processes.append(process)

            rank += len(ids)
    # --host is not specified: single node is used
    else:
        if args.log != "-":
            Path(logfile).parent.mkdir(parents=True, exist_ok=True)
            f = logfile.open("w", encoding="utf-8")
        else:
            # Output to stdout/stderr
            f = None
        world_size = args.ngpu
        # Using cmd as it is simply
        cmd = args.args + [
            f"distributed_training.distributed_world_size={world_size}",
            f"distributed_training.nprocs_per_node={world_size}",
            f"hydra.run.dir={str(rundir)}",
        ]
        logging.info(" ".join(cmd))
        print(" ".join(cmd), file=f, flush=True)
        process = subprocess.Popen(cmd, stdout=f, stderr=f)
        processes.append(process)

    if args.log != "-":
        logging.info(f"log file: {logfile}")

    failed = False
    while any(p.returncode is None for p in processes):
        for process in processes:
            # If any process is failed, try to kill the other processes too
            if failed and process.returncode is not None:
                process.kill()
            else:
                try:
                    process.wait(0.5)
                except subprocess.TimeoutExpired:
                    pass

                if process.returncode is not None and process.returncode != 0:
                    failed = True

    for process in processes:
        if process.returncode != 0:
            print(
                subprocess.CalledProcessError(returncode=process.returncode, cmd=cmd),
                file=sys.stderr,
            )
            p = Path(logfile)
            if p.exists():
                with p.open() as f:
                    lines = list(f)
                raise RuntimeError(
                    f"\n################### The last 1000 lines of {logfile} "
                    f"###################\n" + "".join(lines[-1000:])
                )
            else:
                raise RuntimeError


if __name__ == "__main__":
    main()
