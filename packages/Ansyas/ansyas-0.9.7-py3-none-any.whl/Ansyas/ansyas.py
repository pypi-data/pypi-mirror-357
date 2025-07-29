import os

import MAS_models as MAS
import shutil
import pyaedt
import typing
import excitation
import ansyas_utils
import bobbin as bobbin_builder
import core as core_builder
import cooling as cooling_builder
import coil as coil_builder
import excitation as excitation_builder
import outputs

from pyaedt.modeler.cad.object3d import Object3d


class Ansyas:

    def __init__(self, number_segments_arcs=12, initial_mesh_configuration=5, maximum_error_percent=3, maximum_passes=40, refinement_percent=30, scale=1):
        self.initial_mesh_configuration = initial_mesh_configuration
        self.number_segments_arcs = number_segments_arcs
        self.maximum_error_percent = maximum_error_percent
        self.refinement_percent = refinement_percent
        self.maximum_passes = maximum_passes
        self.scale = scale
        self.bobbin_builder = None
        self.core_builder = None
        self.cooling_builder = None
        self.coil_builder = None
        self.outputs_extractor = None
        self.padding = {
            "x_pos": 100,
            "y_pos": 100,
            "z_pos": 100,
            "x_neg": 100,
            "y_neg": 100,
            "z_neg": 100,
        }

    def fit(self):
        self.project.modeler.fit_all()

    def analyze(self):
        self.project.analyze()

    def set_units(self, units):
        """Sets the units of the modeler.

        Parameters
        ----------
        units : str
            Units to sue in the model of the magnetic.


        Examples
        --------
        Sets units to meters.


        >>> ansyas.set_units("meter")

        """
        self.project.modeler.model_units = units

    def create_project(self, outputs_folder, project_name, non_graphical=False, new_desktop_session=False, solution_type="EddyCurrent", specified_version=None):
        """Create a project for the given inputs.

        Configures Ansyas and create an Ansys project with the requested inputs.

        Parameters
        ----------
        mas : MAS.Mas, dict
            Mas file or dict containing the information about the magnetic, its
            inputs, and outputs.
        non_graphical : str
            Path to store the output project.
        project_name : str
            Name of the project.
        non_graphical : bool
            Whether to launch AEDT in non-graphical mode. The default
            is ``False``, in which case AEDT is launched in graphical
            mode. This parameter is ignored when a script is launched within
            AEDT.
        non_graphical : bool, optional
            Whether to launch AEDT in non-graphical mode. The default
            is ``False``, in which case AEDT is launched in graphical
            mode. This parameter is ignored when a script is launched within
            AEDT.
        new_desktop_session : bool, optional
            Whether to launch an instance of AEDT in a new thread, even if
            another instance of the ``specified_version`` is active on the
            machine. The default is ``False``. This parameter is ignored
            when a script is launched within AEDT.
        solution_type : str, optional
            Solution type to apply to the design. The default is
            ``EddyCurrent``.
        specified_version : str
            Version of AEDT  to use.

        Examples
        --------
        Creates an Icepak design.


        >>> from src.ansyas import Ansyas
        >>> project = ansyas.create_project(
            outputs_folder=outputs_folder,
            project_name=project_name,
            non_graphical=non_graphical,
            solution_type="SteadyState",
            new_desktop_session=new_desktop_session
        )

        """
        project_name = f"{project_name}.aedt"
        self.project_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), outputs_folder)

        # shutil.rmtree(self.project_path, ignore_errors=True)
        os.makedirs(self.project_path, exist_ok=True)
        # self.project_name = os.path.join(self.project_path, project_name)
        self.solution_type = solution_type
        self.project_name = project_name
        self.project_name = self.project_name.replace(" ", "_").replace(",", "_").replace(":", "_").replace("/", "_").replace("\\", "_")

        if not os.path.exists(self.project_path):
            os.makedirs(self.project_path)

        if self.solution_type == "SteadyState":
            self.project = pyaedt.Icepak(
                project=self.project_name,
                solution_type="SteadyState",
                non_graphical=non_graphical,
                specified_version=specified_version,
                new_desktop=new_desktop_session,
                close_on_exit=False
            )

        else:
            self.project = pyaedt.Maxwell3d(
                project=self.project_name,
                solution_type=solution_type,
                non_graphical=non_graphical,
                specified_version=specified_version,
                new_desktop=new_desktop_session,
                close_on_exit=False
            )
            self.project.change_design_settings({"ComputeTransientCapacitance": True})
            self.project.change_design_settings({"ComputeTransientInductance": True})
            self.project.mesh.assign_initial_mesh_from_slider(self.initial_mesh_configuration, curvilinear=True)

        self.project.autosave_disable()

        return self.project

    def move(self, object3D: Object3d, vector: typing.List[float]):
        if isinstance(object3D, list):
            result = True
            for elem in object3D:
                result = result and elem.move(self.convert_units(vector))
            return result
        else:
            return object3D.move(self.convert_units(vector))

    def rotate(self, object3D: Object3d, axis, angle):
        return object3D.rotate(axis=axis, angle=angle)
    
    def clone(self, object3D: Object3d):
        result, objects = self.project.modeler.clone(object3D)
        if result:
            if isinstance(object3D, list):
                return [self.project.modeler.get_object_from_name(x) for x in objects]
            else:
                return self.project.modeler.get_object_from_name(objects[0])
        else:
            return None

    def create_non_model_rectangle(self, width, height, orientation, center, name=None):
        if orientation is pyaedt.constants.PLANE.YZ:
            origin = [0, center[0] - width / 2, center[1] - height / 2]
        elif orientation is pyaedt.constants.PLANE.XY:
            origin = [center[0] - width / 2, center[1] - height / 2, 0]
        elif orientation is pyaedt.constants.PLANE.ZX:
            origin = [center[0] - width / 2, 0, center[1] - height / 2]
        rectangle = self.project.modeler.create_rectangle(
            origin=self.convert_units(origin),
            sizes=self.convert_units([width, height]),
            name=name,
            orientation=orientation,
            non_model=True
        )
        rectangle.model = False

        if isinstance(rectangle, str):
            return self.project.modeler.get_object_from_name(rectangle)
        else:
            return rectangle

    def create_builders(self, magnetic: MAS.Magnetic):
        self.core_builder = core_builder.Core(
            project=self.project, 
        )
        self.cooling_builder = cooling_builder.Cooling(
            project=self.project, 
        )
        self.bobbin_builder = bobbin_builder.Bobbin(
            project=self.project, 
            number_segments_arcs=self.number_segments_arcs
        )

        if self.solution_type == "Electrostatic":
            if magnetic.core.functionalDescription.shape.family is MAS.CoreShapeFamily.t:
                self.coil_builder = coil_builder.ToroidalCoil(
                    project=self.project, 
                    number_segments_arcs=self.number_segments_arcs,
                    add_insulation=True
                )
            else:
                self.coil_builder = coil_builder.ConcentricSpiralCoil(
                    project=self.project, 
                    number_segments_arcs=self.number_segments_arcs,
                    add_insulation=True
                )
        else:
            if magnetic.core.functionalDescription.shape.family is MAS.CoreShapeFamily.t:
                self.coil_builder = coil_builder.ToroidalCoil(
                    project=self.project, 
                    number_segments_arcs=self.number_segments_arcs,
                    add_insulation=False
                )
            else:
                self.coil_builder = coil_builder.ConcentricCoil(
                    project=self.project, 
                    number_segments_arcs=self.number_segments_arcs,
                    add_insulation=False
                )

        self.excitation_builder = excitation_builder.Excitation(
            project=self.project, 
        )
        self.outputs_extractor = outputs.Outputs(
            project=self.project, 
        )

    def create_boundary_region(self, padding=None):
        if padding is None:
            region = self.project.modeler.create_air_region(x_pos=50, y_pos=50, z_pos=50, x_neg=50, y_neg=50, z_neg=50)
            if region is None or region is False:
                region = self.project.modeler.get_objects_w_string("Region")
                region = self.project.modeler.get_object_from_name(region[0])

            return region
        else:
            region = self.project.modeler.create_region(pad_percent=[padding["x_pos"], padding["x_neg"], padding["y_pos"], padding["y_neg"], padding["z_pos"], padding["z_neg"]], is_percentage=True)
            if region is None or region is False:
                region = self.project.modeler.get_objects_w_string("Region")
                region = self.project.modeler.get_object_from_name(region[0])

            return region

    def create_boundary_conditions(self, conditions):
        region = self.project.modeler.get_objects_w_string("Region")
        region = self.project.modeler.get_object_from_name(region[0])

        if conditions.cooling is None or conditions.cooling.velocity is None:
            faces = region.faces
            self.project.assign_pressure_free_opening(
                boundary_name="AirOpening",
                assignment=[int(str(x)) for x in faces]
            )
        else:
            velocity = ansyas_utils.convert_axis(conditions.cooling.velocity)
            self.project.assign_free_opening(
                boundary_name="AirOpening",
                assignment=region.bottom_face_x,
                flow_type="Pressure",
                velocity=[f"{velocity[0]}m_per_sec", f"{velocity[1]}m_per_sec", f"{velocity[2]}m_per_sec"],
                temperature="AmbientTemp" if conditions.cooling.temperature is None else conditions.cooling.temperature,
            )
            self.project.assign_free_opening(
                assignment=[int(str(x)) for x in faces if x != region.bottom_face_x],
                flow_type="Pressure",
                velocity=[f"{velocity[0]}m_per_sec", f"{velocity[1]}m_per_sec", f"{velocity[2]}m_per_sec"],
                temperature="AmbientTemp" if conditions.cooling.temperature is None else conditions.cooling.temperature,
            )

    def create_setup(self, frequency: float = 100000, ):
        setup = self.project.create_setup("Setup")
        if self.project.solution_type == "Transient" or self.project.solution_type == "TransientAPhiFormulation":
            setup.props["StopTime"] = f"{2 / frequency}s"
            setup.props["TimeStep"] = f"{2 / frequency / 10}s"
        elif self.project.solution_type == "EddyCurrent":

            setup.props["Frequency"] = f"{frequency * 3}"
            setup.props["PercentRefinement"] = self.refinement_percent
            setup.props["MaximumPasses"] = self.maximum_passes
            setup.props["PercentError"] = self.maximum_error_percent
            setup.props["HasSweepSetup"] = True

            setup.add_eddy_current_sweep(
                sweep_type="LinearStep",
                start_frequency=frequency,
                stop_frequency=frequency * 4,
                step_size=frequency * 2,
                units="Hz",
                clear=True,
                save_all_fields=True
            )

            self.frequency = frequency
        elif self.project.solution_type == "Electrostatic":

            setup.props["Frequency"] = f"{frequency * 3}"
            setup.props["PercentRefinement"] = self.refinement_percent
            setup.props["MaximumPasses"] = 40
            setup.props["PercentError"] = self.maximum_error_percent
            self.frequency = frequency

    def add_skin_effect(self, wires_faces, skin_depth: float = 0.0002, number_layers=2):
        if not isinstance(wires_faces, list):
            wires_faces = [wires_faces]
        self.project.mesh.assign_skin_depth(
            wires_faces,
            skin_depth=f"{self.convert_units(skin_depth)}mm",
            maximum_elements=None,
            # triangulation_max_length="0.1mm",
            layers_number=number_layers,
            # name=None
        )

    def create_magnetic_simulation(self, mas: [MAS.Mas, dict], simulate=False, operating_point_index=0):
        """Create an automatic simulation form the mas file.

        Parameters
        ----------
        mas : MAS.Mas, dict
            Mas file or dict containing the information about the magnetic, its
            inputs, and outputs.
        simulate : bool, optional
            Runs the simulation and capture outputs if true. The default
            is ``False``, 


        Examples
        --------
        Import a MAS file from a json and simulate its temperature.
        

        >>> import json
        >>> import os

        >>> f = open("tests/mas_files/simple_inductor_round_column.json)
        >>> mas_dict = json.load(f)

        >>> outputs_folder = os.path.dirname(__file__) + "/outputs"
        >>> outputs_folder = "example"

        >>> project = ansyas.create_project(
            outputs_folder=outputs_folder,
            project_name=project_name,
            solution_type="SteadyState",
        )
        >>> ansyas.set_units("meter")
        >>> ansyas.create_magnetic_simulation(
            mas=mas,
            simulate=True
        )


        """
        if isinstance(mas, dict):
            mas = MAS.Mas.from_dict(mas)

        magnetic = mas.magnetic
        inputs = mas.inputs
        outputs = mas.outputs

        self.create_builders(magnetic)

        core_parts = self.core_builder.import_core(
            core=magnetic.core,
            operating_point=inputs.operatingPoints[operating_point_index],
        )

        if self.solution_type in "SteadyState":
            core_losses = outputs[operating_point_index].coreLosses.coreLosses
            self.core_builder.assign_core_losses_as_heat_source(core_parts, core_losses)
            self.cooling_builder.create_cooling(magnetic.core, inputs.operatingPoints[operating_point_index].conditions.cooling)

        self.fit()

        bobbin = self.bobbin_builder.create_simple_bobbin(
            bobbin=magnetic.coil.bobbin,
            material="Plastic" if self.solution_type == "SteadyState" else "PVC plastic",  # TODO: Create material from bobbin
        )

        turns_and_terminals = self.coil_builder.create_coil(
            coil=magnetic.coil,
        )

        for core_part in core_parts:
            if bobbin is not None:
                bobbin.subtract(core_part, True)
                for aux in turns_and_terminals:
                    if isinstance(aux, tuple):
                        [turn, terminal] = aux
                    else:
                        turn = aux
                    bobbin.subtract(turn, True)

            for aux in turns_and_terminals:
                if isinstance(aux, tuple):
                    [turn, terminal] = aux
                else:
                    turn = aux
                core_part.subtract(turn, True)

        winding_losses = outputs[operating_point_index].windingLosses.windingLossesPerTurn

        if self.solution_type in "SteadyState":
            self.coil_builder.assign_turn_losses_as_heat_source(turns_and_terminals, winding_losses)

        if self.solution_type in ["EddyCurrent", "Transient", "TransientAPhiFormulation"]:
            self.excitation_builder.add_excitation(
                coil=magnetic.coil,
                turns_and_terminals=turns_and_terminals,
                operating_point=inputs.operatingPoints[operating_point_index],
            )

        if self.solution_type in "SteadyState":
            self.create_boundary_conditions(inputs.operatingPoints[operating_point_index].conditions)
        else:
            self.create_boundary_region(self.padding)

        self.create_setup(inputs.operatingPoints[operating_point_index].excitationsPerWinding[0].frequency)
        if self.solution_type in "SteadyState":
            self.project.globalMeshSettings(
                meshtype=1
            )

        self.fit()

        if simulate:
            self.analyze()
            self.outputs_extractor.get_results()
            self.project.release_desktop(close_projects=False, close_desktop=False)
