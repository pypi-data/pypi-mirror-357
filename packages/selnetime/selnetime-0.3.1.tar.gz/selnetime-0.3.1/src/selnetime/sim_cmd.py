import os
import argparse
import numpy as np
from . import simulator
import random


def restricted_x0(x):
    if x == "uniform":
        return x
    else:
        try:
            x = float(x)
        except ValueError:
            raise argparse.ArgumentTypeError("%r not a floating-point literal" % (x,))

        if x < 0.0 or x > 1.0:
            raise argparse.ArgumentTypeError("%r not in range [0.0, 1.0]" % (x,))
    return x


def restricted_depth(x):
    if isinstance(x, str):
        # Check if the string is a comma-separated list
        if "," in x:
            # Try to split and convert each element to an integer
            try:
                values = [int(item) for item in x.split(",")]
            except ValueError:
                raise argparse.ArgumentTypeError(f"{x!r} contains non-integer values")

            # Check for negative values in the list
            for value in values:
                if value < 0:
                    raise argparse.ArgumentTypeError(f"{x!r} contains negative values")
            return values
        else:
            # Try to convert a single string to an integer
            try:
                x = int(x)
            except ValueError:
                raise argparse.ArgumentTypeError(f"{x!r} not an int")
    else:
        # If x is not a string, try to convert it to an integer directly
        try:
            x = int(x)
        except ValueError:
            raise argparse.ArgumentTypeError(f"{x!r} not an int")

    if x < 0:
        raise argparse.ArgumentTypeError(f"{x!r} should not be negative")

    return [x]


def snt_sim_param():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-times",
        "--sampling_time",
        type=lambda s: [int(item) for item in s.split(",")],
        required=True,
        help="Comma-separated list of integers (e.g., 1,2,3,4) for the sampling times",
    )
    parser.add_argument("-N", "--Ne", type=int, required=True)
    parser.add_argument("-S", "--S", type=float, required=True)
    parser.add_argument("-H", "--H", type=float, required=True)
    parser.add_argument("-x0", "--x0", type=restricted_x0, required=True)
    parser.add_argument("-depth", "--depth", type=restricted_depth, required=True)
    parser.add_argument(
        "-nrep",
        "--nrep",
        type=int,
        help="Number of simulation to be added to the file",
        required=True,
    )
    parser.add_argument("-working_directory", "--working_directory", type=str)
    parser.add_argument("-seed", "--seed", type=int)
    args = parser.parse_args()

    sampling_time = args.sampling_time
    N = args.Ne
    S = args.S
    H = args.H
    x0 = (
        args.x0
    )  # should accept values and string (values in ]0,1[ and string : uniform)
    depth = args.depth  # possibilty to give a depth vector in a file
    nrep = args.nrep  # Number of simulations
    working_directory = args.working_directory
    seed = args.seed

    if working_directory is None:
        working_directory = os.getcwd()

    # Generate a seed if not provided by the user.
    if seed is None:
        seed = int(np.random.randint(12345789, size=1)[0])
        np.random.seed(seed)
    print(f"Seed : {seed}")

    if working_directory[-1] != "/":
        working_directory += "/"

    if not isinstance(sampling_time, np.ndarray):
        sampling_time = np.array(sampling_time)
    file_name = os.path.basename(os.path.normpath(working_directory))
    file_path = working_directory + file_name
    if len(depth) == 1:
        depth_vect = np.ones_like(sampling_time) * depth
    elif not isinstance(depth, np.ndarray):
        depth_vect = np.array(depth)
    if len(depth_vect) != len(sampling_time):
        raise ValueError("The length of depth_vect should be the same as sampling_time")
    params = {
        "ID_simu": file_name,
        "h": H,
        "N": N,
        "s": S,
        "x0": x0,
        "sampling_time": sampling_time,
        "depth_vect": depth_vect,
        "seed": seed,
        "nrep": nrep,
    }
    simulator.create_param_file(params, file_path=file_path)


def snt_sim():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-yaml",
        "--yaml_file",
        type=str,
        help="Path to the yaml file containing the parameters for the simulation",
        required=True,
    )
    parser.add_argument(
        "-ft",
        "--file_type",
        type=str,
        default="baypass",
        help=argparse.SUPPRESS,
        choices=["csv", "baypass"],
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        nargs="?",
        const="",
        default=None,
        help="Specify a different output, default is prefix. If OUTPUT is set "
            "empty, no file will be created and some data will be lost. If "
            "OUTPUT is set to \"/dev/stdout\" or just \"stdout\", the "
            "information in the files will be printed on terminal"
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        default=False,
        help="Disable every log in stdout "
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Specify a seed to use"
    )
    args = parser.parse_args()
    yaml_file_path = args.yaml_file
    file_type = args.file_type
    seed = args.seed

    data = simulator.parse_file(yaml_file_path)
    x0 = data["x0"]
    sampling_time = data["sampling_time"]
    depth_vect = data["depth_vect"]
    Ne = data["N"]
    s = data["s"]
    h = data["h"]
    nbr_traj = data["nrep"]
    p = data["proportion_sel"]

    if seed == None:
        try:
            seed = data["seed"]
        except:
            seed = int(np.random.randint(12345789, size=1)[0])

    if not args.quiet:
        print(
            "Parameters for the simulator : \n"
            + f"x0 : {x0} \n"
            + f"sampling_time : {sampling_time} \n"
            + f"depth : {depth_vect} \n"
            + f"Ne : {Ne} \n"
            + f"s : {s} \n"
            + f"h : {h} \n"
            + f"seed : {seed} \n"
            + f"nrep : {nbr_traj} \n"
            + f"proportion_sel : {p} \n"
        )

    folder_path = os.path.dirname(yaml_file_path)
    file_name_with_extension = os.path.basename(yaml_file_path)
    file_name, file_extension = os.path.splitext(file_name_with_extension)
    if args.output is not None and args.output != "" :
        file_name = args.output

    if folder_path != "":
        working_directory = folder_path + "/"
    else:
        working_directory = os.getcwd() + "/"

    filename = working_directory + file_name
    simulator.create_trajectories_simulations(
        yaml_file_path, filename, seed, file_type=file_type
    )
    if not args.quiet:
        print(f"Data has been added to {file_name}.{file_type}")

    # Convert the sampling times to a comma-separated string
    sampling_time = ",".join(map(str, sampling_time))

    # Write the sampling times to a text file
    sampling_path = filename + ".times"
    with open(sampling_path, "w") as f:
        f.write(sampling_time)
    if not args.quiet:
        print(f"File {sampling_path} created successfully.")
