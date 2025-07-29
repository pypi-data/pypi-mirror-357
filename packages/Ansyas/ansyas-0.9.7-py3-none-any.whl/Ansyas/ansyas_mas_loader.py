import json
import os
import time
import sys

sys.path.append(os.path.dirname(__file__))

import mas_autocomplete
from ansyas import Ansyas


if __name__ == "__main__":
    non_graphical = False
    new_desktop_session = False

    f = open(sys.argv[1])
    mas_dict = json.load(f)

    mas = mas_autocomplete.autocomplete(mas_dict)
    if len(sys.argv) > 2:
        operating_point_index = int(sys.argv[2])
        assert operating_point_index < len(mas.inputs.operatingPoints), f"Operating point {operating_point_index} is not present on inputs, which only have {len(mas.inputs.operatingPoints)} points"
    else:
        operating_point_index = 0

    if len(sys.argv) > 3:
        solution_type = str(sys.argv[3])
        assert solution_type in ["SteadyState", "EddyCurrent", "Transient", "TransientAPhiFormulation"], "solution type must be one of SteadyState, EddyCurrent, Transient, TransientAPhiFormulation"
    else:
        solution_type = "EddyCurrent"

    if len(sys.argv) > 4:
        number_segments_arcs = int(sys.argv[4])
    else:
        number_segments_arcs = 12

    if len(sys.argv) > 5:
        outputs_folder = str(sys.argv[5])
    else:
        outputs_folder = os.path.dirname(__file__) + "/outputs"

    if len(sys.argv) > 6:
        project_name = str(sys.argv[6])
    else:
        try:
            project_name = f"{mas_dict['magnetic']['manufacturerInfo']['reference']}_{time.time()}"
        except TypeError:
            project_name = f"Unnamed_design_{time.time()}"

    ansyas = Ansyas(number_segments_arcs=number_segments_arcs, initial_mesh_configuration=2, maximum_error_percent=5, refinement_percent=5, scale=1)

    print("outputs_folder")
    print(outputs_folder)
    print("project_name")
    print(project_name)

    project = ansyas.create_project(
        outputs_folder=outputs_folder,
        project_name=project_name,
        # specified_version="2023.2",
        non_graphical=non_graphical,
        solution_type=solution_type,
        new_desktop_session=new_desktop_session
    )
    ansyas.set_units("meter")
    ansyas.create_magnetic_simulation(
        mas=mas,
        simulate=True,
        operating_point_index=operating_point_index
    )
