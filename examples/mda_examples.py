#!/usr/bin/env python3
"""
Example: Using Native useq-schema MDA with imswitchclient

This example demonstrates how to create and execute native useq-schema MDASequence
protocols from a Jupyter notebook or Python script, sending them to ImSwitch via
the REST API using the imswitchclient library.

This follows the pattern requested by @beniroquai - formulate protocols outside
ImSwitch runtime and send them via REST API for execution.

Requirements:
    pip install useq-schema imswitchclient
"""

import json
from typing import Dict, Any

hosturl = "100.104.189.88"  # Change to your ImSwitch server address
# Import the imswitchclient

import imswitchclient.ImSwitchClient as imc

try:
    from useq import MDASequence, Channel, TIntervalLoops, ZRangeAround, AbsolutePosition, GridRowsColumns, RelativePosition
    HAS_USEQ = True
except ImportError:
    print("Error: useq-schema not installed")
    print("Install with: pip install useq-schema")
    HAS_USEQ = False


def example_1_simple_xyz_timelapse():
    """
    Example 1: Simple XYZ time-lapse scan.
    
    This creates a multi-position, Z-stack time-lapse using the imswitchclient
    library with native useq-schema MDASequence objects.
    """
    if not HAS_USEQ:
        return
    
    print("=" * 70)
    print("Example 1: XYZ Time-Lapse Scan")
    print("=" * 70)
    print()
    
    # Define the MDA sequence
    sequence = MDASequence(
        metadata={
            "experiment": "xyz_timelapse",
            "description": "Multi-position Z-stack time-lapse",
            "user": "researcher"
        },
        grid_plan={"rows": 2, "columns": 2, "fov_width": 200.0, "fov_height": 200.0},
        channels=[
            Channel(config="LED", exposure=10.0)
        ],
        stage_positions=[(1, 1, 1)],
        z_plan=ZRangeAround(range=10.0, step=2.0),  # 10µm range, 2µm steps
        time_plan=TIntervalLoops(interval=60.0, loops=10),  # 10 timepoints, 1 min apart
        axis_order="tpgcz"  # time, position, z, channel
    )
    



    # print each event in the sequence
    for event in sequence:
        print(event)


    print(f"Created MDA sequence:")
    print(f"  3 positions × 6 Z-slices × 10 timepoints = {len(list(sequence))} events")
    print(f"  Axis order: {sequence.axis_order}")
    print(f"  Metadata: {sequence.metadata}")
    print()
    
    # Connect to ImSwitch
    client = imc.ImSwitchClient(host=hosturl, port=8001)
    
    # Check if MDA is available
    caps = client.mdaController.check_mda_available()
    if not caps.get('mda_available'):
        print("❌ MDA functionality not available on server")
        return

    
    # Get sequence info before executing
    # info = client.mdaController.get_mda_sequence_info(sequence)
    # print(f"Sequence preview:")
    # print(f"  Total events: {info.get('total_events', 'N/A')}")
    # print(f"  Estimated duration: {info.get('estimated_duration_minutes', 0):.1f} minutes")
    # print()
    
    # Execute the sequence
    print("Starting MDA experiment")
    result = client.mdaController.run_native_mda_sequence(sequence)
    print(f"✓ Result: {result}")
    print()


def example_2_multi_channel_zstack():
    """
    Example 2: Multi-channel Z-stack at multiple positions.
    """
    if not HAS_USEQ:
        return
    
    print("=" * 70)
    print("Example 2: Multi-Channel Z-Stack at Multiple Positions")
    print("=" * 70)
    print()
    
    sequence = MDASequence(
        metadata={
            "experiment": "multi_channel_zstack",
            "sample": "cells_sample_01"
        },
        stage_positions=[
            AbsolutePosition(x=0.0, y=0.0, z=10.0),
            AbsolutePosition(x=100.0, y=0.0, z=10.0)
        ],
        channels=[
            Channel(config="DAPI", exposure=50.0),
            Channel(config="FITC", exposure=100.0),
            Channel(config="TRITC", exposure=150.0)
        ],
        z_plan=ZRangeAround(range=20.0, step=2.0),  # 20µm range, 2µm steps
        axis_order="pczg"  # position, channel, z
    )
    
    print(f"Created MDA sequence:")
    print(f"  2 positions × 3 channels × 11 Z-slices = {len(list(sequence))} events")
    print(f"  Axis order: {sequence.axis_order}")
    print()
    
    # Show the sequence as JSON (what gets sent to the API)
    print("Sequence as JSON (first 500 chars):")
    sequence_json = json.dumps(
        sequence.model_dump() if hasattr(sequence, 'model_dump') else sequence.dict(), 
        indent=2
    )
    print(sequence_json[:500] + "")
    print()
    
    # To execute:
    client = imc.ImSwitchClient(host=hosturl, port=8001)
    # result = client.mdaController.run_native_mda_sequence(sequence)
    print("To execute, uncomment: result = client.mdaController.run_native_mda_sequence(sequence)")
    print()


def example_3_timelapse_with_autofocus():
    """
    Example 3: Time-lapse with autofocus metadata.
    
    Note: Autofocus execution would need to be handled by ImSwitch's
    autofocus hooks in the MDASequenceManager.
    """
    if not HAS_USEQ:
        return
    
    print("=" * 70)
    print("Example 3: Time-Lapse with Autofocus Metadata")
    print("=" * 70)
    print()
    
    sequence = MDASequence(
        metadata={
            "experiment": "timelapse_autofocus",
            "autofocus": {
                "enabled": True,
                "frequency": "every_position",  # Run at each position
                "method": "software"
            }
        },
        stage_positions=[
            AbsolutePosition(x=i*100.0, y=i*50.0, z=10.0)
            for i in range(4)
        ],
        channels=[
            Channel(config="Brightfield", exposure=10.0)
        ],
        time_plan=TIntervalLoops(interval=300.0, loops=20),  # 20 timepoints, 5 min apart
        axis_order="tpc"
    )
    
    print(f"Created MDA sequence:")
    print(f"  4 positions × 20 timepoints = {len(list(sequence))} events")
    print(f"  Autofocus metadata: {sequence.metadata.get('autofocus')}")
    print()
    
    # To execute:
    client = imc.ImSwitchClient(host=hosturl, port=8001)
    # result = client.mdaController.run_native_mda_sequence(sequence)


def example_4_simple_experiment_dict():
    """
    Example 4: Using simplified dict-based experiment configuration.
    
    This alternative approach uses a simpler dict format instead of
    full useq-schema objects.
    """
    print("=" * 70)
    print("Example 4: Simplified Dict-Based Configuration")
    print("=" * 70)
    print()
    
    experiment = {
        "channels": [
            {"name": "LED", "exposure": 10.0, "power": 100.0},
            {"name": "LASER", "exposure": 5.0, "power": 80.0}
        ],
        "z_range": 10.0,       # 10 µm Z range
        "z_step": 2.0,         # 2 µm steps
        "time_points": 5,      # 5 time points
        "time_interval": 60.0, # Every 1 minute
        "experiment_name": "Simple_Experiment"
    }
    
    print("Experiment configuration:")
    print(json.dumps(experiment, indent=2))
    print()
    
    # Connect and execute
    client = imc.ImSwitchClient(host=hosturl, port=8001)
    
    # Get preview
    # info = client.mdaController.get_mda_sequence_info(experiment)
    # print(f"Estimated duration: {info.get('estimated_duration_minutes', 0):.1f} minutes")
    
    # Execute
    # result = client.mdaController.start_mda_experiment(experiment)
    # print(f"Started: {result}")
    print("To execute, uncomment the execution lines above")
    print()


def example_5_monitoring_experiment():
    """
    Example 5: Start experiment and monitor its progress.
    """
    if not HAS_USEQ:
        return
    
    print("=" * 70)
    print("Example 5: Start and Monitor Experiment")
    print("=" * 70)
    print()
    
    # Simple sequence
    sequence = MDASequence(
        metadata={"experiment": "monitoring_demo"},
        channels=[Channel(config="Brightfield", exposure=10.0)],
        z_plan=ZRangeAround(range=5.0, step=1.0),
        time_plan=TIntervalLoops(interval=30.0, loops=3),
        axis_order="tzc"
    )
    
    client = imc.ImSwitchClient(host=hosturl, port=8001)
    
    print("Starting experiment")
    # result = client.mdaController.run_native_mda_sequence(sequence)
    # print(f"Started: {result}")
    
    print("\nTo monitor progress:")
    print("  status = client.mdaController.get_mda_status()")
    print("  print(f\"Progress: {status.get('progress_percent', 0):.1f}%\")")
    
    print("\nTo pause:")
    print("  client.mdaController.pause_mda_experiment()")
    
    print("\nTo resume:")
    print("  client.mdaController.resume_mda_experiment()")
    
    print("\nTo stop:")
    print("  client.mdaController.stop_mda_experiment()")
    print()


def main():
    """Run all examples."""
    print()
    print("=" * 70)
    print("Native useq-schema MDA with imswitchclient Examples")
    print("=" * 70)
    print()
    print("These examples show how to create MDA sequences in a Jupyter notebook")
    print("or Python script and execute them on ImSwitch via the imswitchclient.")
    print()
    
    if not HAS_USEQ:
        return
    
    # Run examples
    example_1_simple_xyz_timelapse()
    #example_2_multi_channel_zstack()
    #example_3_timelapse_with_autofocus()
    #example_4_simple_experiment_dict()
    #example_5_monitoring_experiment()
    
    print("=" * 70)
    print("Summary")
    print("=" * 70)
    print()
    print("✓ Create MDA sequences with native useq-schema objects")
    print("✓ Send to ImSwitch via imswitchclient.mdaController")
    print("✓ Works from Jupyter notebooks, Python scripts")
    print("✓ Protocol-compatible with pymmcore-plus and other useq systems")
    print("✓ Monitor and control experiment execution")
    print()
    print("API Reference:")
    print("  client.mdaController.check_mda_available()")
    print("  client.mdaController.run_native_mda_sequence(sequence)")
    print("  client.mdaController.get_mda_sequence_info(sequence)")
    print("  client.mdaController.start_mda_experiment(experiment)")
    print("  client.mdaController.get_mda_status()")
    print("  client.mdaController.pause_mda_experiment()")
    print("  client.mdaController.resume_mda_experiment()")
    print("  client.mdaController.stop_mda_experiment()")
    print()


if __name__ == "__main__":
    main()
