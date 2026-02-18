"""
MDA Controller for ImSwitch Client

This module provides a client interface for Multi-Dimensional Acquisition (MDA)
functionality using the useq-schema standard.

Example usage:
    from imswitchclient import ImSwitchClient
    from useq import MDASequence, Channel, ZRangeAround
    
    client = ImSwitchClient('localhost', port=8001)
    
    # Create MDA sequence
    sequence = MDASequence(
        channels=[Channel(config="LED", exposure=10.0)],
        z_plan=ZRangeAround(range=10.0, step=2.0)
    )
    
    # Execute via mdaController
    result = client.mdaController.run_mda_sequence(sequence)
"""

from typing import Dict, Any, Optional


class mdaController(object):
    """
    REST API interface for MDA (Multi-Dimensional Acquisition) Controller.
    
    This controller allows you to create and execute native useq-schema MDASequence
    protocols from a Jupyter notebook or Python script, sending them to ImSwitch via
    the REST API.
    """

    def __init__(self, parent):
        self.parent = parent

    def check_mda_available(self) -> Dict[str, Any]:
        """
        Check if MDA functionality is available on the server.
        
        Returns:
            dict: Capabilities information including:
                - mda_available: bool indicating if MDA is available
                - available_channels: list of available channel configurations
                - stage_available: bool indicating if stage is available
                - autofocus_available: bool indicating if autofocus is available
        """
        url = f"{self.parent.base_uri}/ExperimentController/get_mda_capabilities"
        headers = {"accept": "application/json"}
        return self.parent.get_json(url, headers=headers)

    def run_native_mda_sequence(self, sequence) -> Dict[str, Any]:
        """
        Execute a native useq-schema MDASequence on ImSwitch.
        
        Args:
            sequence: Native useq.MDASequence object or dict
            
        Returns:
            dict: Response with execution status and info including:
                - status: 'started', 'error', etc.
                - save_directory: Path where data will be saved
                - estimated_duration_minutes: Estimated time to complete
                - total_events: Number of acquisition events
                
        Example:
            from useq import MDASequence, Channel, ZRangeAround
            
            sequence = MDASequence(
                channels=[Channel(config="LED", exposure=10.0)],
                z_plan=ZRangeAround(range=10.0, step=2.0)
            )
            
            result = client.mdaController.run_native_mda_sequence(sequence)
        """
        # Convert MDASequence to dict/JSON if needed
        # Use mode='json' to properly serialize Enums and other non-JSON types
        if hasattr(sequence, 'model_dump'):
            sequence_dict = sequence.model_dump(mode='json')
        elif hasattr(sequence, 'dict'):
            sequence_dict = sequence.dict()
        else:
            sequence_dict = sequence
            
        url = f"{self.parent.base_uri}/ExperimentController/run_native_mda_sequence"
        headers = {
            "accept": "application/json",
            "Content-Type": "application/json"
        }
        return self.parent.post_json(url, payload=sequence_dict, headers=headers)

    def get_mda_sequence_info(self, sequence) -> Dict[str, Any]:
        """
        Get information about a sequence without executing it.
        
        This is useful for previewing what the sequence will do.
        
        Args:
            sequence: Native useq.MDASequence object or dict
            
        Returns:
            dict: Sequence information including:
                - total_events: Total number of acquisition events
                - axis_order: Order of axes (e.g., 'tpzc')
                - channels: List of channels
                - z_positions: Number of Z positions
                - time_points: Number of time points
                - estimated_duration_minutes: Estimated time
        """
        # Convert MDASequence to dict/JSON if needed
        # Use mode='json' to properly serialize Enums and other non-JSON types
        if hasattr(sequence, 'model_dump'):
            sequence_dict = sequence.model_dump(mode='json')
        elif hasattr(sequence, 'dict'):
            sequence_dict = sequence.dict()
        else:
            sequence_dict = sequence
            
        url = f"{self.parent.base_uri}/ExperimentController/get_mda_sequence_info"
        headers = {
            "accept": "application/json",
            "Content-Type": "application/json"
        }
        return self.parent.post_json(url, payload=sequence_dict, headers=headers)

    def start_mda_experiment(self, experiment: Dict[str, Any]) -> Dict[str, Any]:
        """
        Start an MDA experiment using simplified experiment configuration.
        
        This is an alternative to run_native_mda_sequence that uses a simpler
        dict-based configuration format.
        
        Args:
            experiment: dict with experiment configuration:
                - channels: List of dicts with name, exposure, power
                - z_range: Optional Z range in µm
                - z_step: Optional Z step size in µm
                - time_points: Optional number of time points
                - time_interval: Optional time interval in seconds
                - experiment_name: Name for the experiment
                
        Returns:
            dict: Response with execution status
            
        Example:
            experiment = {
                "channels": [
                    {"name": "LED", "exposure": 10.0, "power": 100.0}
                ],
                "z_range": 10.0,
                "z_step": 2.0,
                "time_points": 5,
                "time_interval": 60.0,
                "experiment_name": "My_Experiment"
            }
            
            result = client.mdaController.start_mda_experiment(experiment)
        """
        url = f"{self.parent.base_uri}/ExperimentController/start_mda_experiment"
        headers = {
            "accept": "application/json",
            "Content-Type": "application/json"
        }
        return self.parent.post_json(url, payload=experiment, headers=headers)

    def stop_mda_experiment(self) -> Dict[str, Any]:
        """
        Stop the currently running MDA experiment.
        
        Returns:
            dict: Response with stop status
        """
        url = f"{self.parent.base_uri}/ExperimentController/stopExperiment"
        headers = {"accept": "application/json"}
        return self.parent.get_json(url, headers=headers)

    def get_mda_status(self) -> Dict[str, Any]:
        """
        Get the status of the current MDA experiment.
        
        Returns:
            dict: Status information including:
                - is_running: bool indicating if experiment is running
                - current_event: Current event number
                - total_events: Total number of events
                - progress_percent: Progress percentage
        """
        url = f"{self.parent.base_uri}/ExperimentController/getExperimentStatus"
        headers = {"accept": "application/json"}
        return self.parent.get_json(url, headers=headers)

    def pause_mda_experiment(self) -> Dict[str, Any]:
        """
        Pause the currently running MDA experiment.
        
        Returns:
            dict: Response with pause status
        """
        url = f"{self.parent.base_uri}/ExperimentController/pauseWorkflow"
        headers = {"accept": "application/json"}
        return self.parent.get_json(url, headers=headers)

    def resume_mda_experiment(self) -> Dict[str, Any]:
        """
        Resume a paused MDA experiment.
        
        Returns:
            dict: Response with resume status
        """
        url = f"{self.parent.base_uri}/ExperimentController/resumeExperiment"
        headers = {"accept": "application/json"}
        return self.parent.get_json(url, headers=headers)
