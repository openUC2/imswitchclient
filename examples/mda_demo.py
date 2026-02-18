#!/usr/bin/env python3
"""
MDA Integration Demo for ImSwitch

This script demonstrates how to use the new MDA (Multi-Dimensional Acquisition)
functionality in ImSwitch using the useq-schema standard and imswitchclient.

Example usage:
    python mda_demo.py --server http://localhost:8001 --demo simple
    python mda_demo.py --server http://localhost:8001 --demo timelapse  
    python mda_demo.py --server http://localhost:8001 --demo full
"""

import json
import argparse
from typing import Dict, Any

from imswitchclient import ImSwitchClient

try:
    from useq import MDASequence, Channel, TIntervalLoops, ZRangeAround
    HAS_USEQ = True
except ImportError:
    print("Error: useq-schema not installed")
    print("Install with: pip install useq-schema")
    HAS_USEQ = False


class MDADemo:
    """Demonstration class for MDA functionality in ImSwitch."""
    
    def __init__(self, server_url: str):
        # Parse server URL
        if "://" in server_url:
            parts = server_url.split("://")[1].split(":")
            host = parts[0]
            port = int(parts[1]) if len(parts) > 1 else 8001
        else:
            parts = server_url.split(":")
            host = parts[0]
            port = int(parts[1]) if len(parts) > 1 else 8001
        
        self.client = ImSwitchClient(host=host, port=port)
        
    def check_capabilities(self) -> Dict[str, Any]:
        """Check if MDA functionality is available."""
        return self.client.mdaController.check_mda_available()
    
    def preview_experiment(self, experiment: Dict[str, Any]) -> Dict[str, Any]:
        """Preview an experiment without running it."""
        return self.client.mdaController.get_mda_sequence_info(experiment)
    
    def start_experiment(self, experiment: Dict[str, Any]) -> Dict[str, Any]:
        """Start an MDA experiment."""
        return self.client.mdaController.start_mda_experiment(experiment)
    
    def demo_simple_zstack(self):
        """Demonstrate a simple Z-stack with two channels."""
        print("=" * 70)
        print("Simple Z-Stack Demo")
        print("=" * 70)
        print()
        
        experiment = {
            "channels": [
                {"name": "LED", "exposure": 50.0, "power": 100.0},
                {"name": "LASER", "exposure": 100.0, "power": 80.0}
            ],
            "z_range": 10.0,  # 10 µm total range
            "z_step": 2.0,    # 2 µm steps  
            "time_points": 1,
            "experiment_name": "Simple_ZStack_Demo"
        }
        
        print("Experiment configuration:")
        print(json.dumps(experiment, indent=2))
        print()
        
        # Preview the experiment
        print("Previewing experiment...")
        preview = self.preview_experiment(experiment)
        if preview:
            print(f"  Total events: {preview.get('total_events', 'N/A')}")
            print(f"  Channels: {preview.get('channels', 'N/A')}")
            print(f"  Z positions: {preview.get('z_positions', 'N/A')}")
            print(f"  Estimated duration: {preview.get('estimated_duration_minutes', 'N/A'):.1f} minutes")
        print()
        
        # Uncomment to actually start the experiment
        print("To start experiment, uncomment:")
        print("  result = self.start_experiment(experiment)")
        print()
        
    def demo_timelapse(self):
        """Demonstrate a time-lapse experiment."""
        print("=" * 70)
        print("Time-Lapse Demo")
        print("=" * 70)
        print()
        
        experiment = {
            "channels": [
                {"name": "Brightfield", "exposure": 10.0, "power": 50.0}
            ],
            "time_points": 10,     # 10 time points
            "time_interval": 30.0, # Every 30 seconds
            "experiment_name": "Timelapse_Demo"
        }
        
        print("Experiment configuration:")
        print(json.dumps(experiment, indent=2))
        print()
        
        # Preview the experiment
        print("Previewing experiment...")
        preview = self.preview_experiment(experiment)
        if preview:
            print(f"  Total events: {preview.get('total_events', 'N/A')}")
            print(f"  Time points: {preview.get('time_points', 'N/A')}")
            print(f"  Estimated duration: {preview.get('estimated_duration_minutes', 'N/A'):.1f} minutes")
        print()
    
    def demo_full_mda(self):
        """Demonstrate a full multi-dimensional experiment."""
        print("=" * 70)
        print("Full Multi-Dimensional Acquisition Demo")
        print("=" * 70)
        print()
        
        experiment = {
            "channels": [
                {"name": "DAPI", "exposure": 50.0, "power": 100.0},
                {"name": "FITC", "exposure": 100.0, "power": 80.0}, 
                {"name": "TRITC", "exposure": 150.0, "power": 90.0}
            ],
            "z_range": 20.0,       # 20 µm Z range
            "z_step": 2.0,         # 2 µm steps
            "time_points": 5,      # 5 time points
            "time_interval": 300.0, # Every 5 minutes
            "experiment_name": "Full_MDA_Demo"
        }
        
        print("Experiment configuration:")
        print(json.dumps(experiment, indent=2))
        print()
        
        # Preview the experiment  
        print("Previewing experiment...")
        preview = self.preview_experiment(experiment)
        if preview:
            print(f"  Total events: {preview.get('total_events', 'N/A')}")
            print(f"  Channels: {preview.get('channels', 'N/A')}")
            print(f"  Z positions: {preview.get('z_positions', 'N/A')}")
            print(f"  Time points: {preview.get('time_points', 'N/A')}")
            print(f"  Estimated duration: {preview.get('estimated_duration_minutes', 'N/A'):.1f} minutes")
        print()

    def demo_native_useq(self):
        """Demonstrate using native useq-schema objects."""
        if not HAS_USEQ:
            print("useq-schema not installed, skipping native useq demo")
            return
        
        print("=" * 70)
        print("Native useq-schema Demo")
        print("=" * 70)
        print()
        
        # Create native useq-schema MDASequence
        sequence = MDASequence(
            metadata={
                "experiment": "native_useq_demo",
                "description": "Using native useq-schema objects"
            },
            channels=[
                Channel(config="LED", exposure=10.0),
                Channel(config="LASER", exposure=5.0)
            ],
            z_plan=ZRangeAround(range=10.0, step=2.0),
            time_plan=TIntervalLoops(interval=60.0, loops=3),
            axis_order="tczg"
        )
        
        print(f"Created native MDASequence:")
        print(f"  Total events: {len(list(sequence))}")
        print(f"  Axis order: {sequence.axis_order}")
        print(f"  Metadata: {sequence.metadata}")
        print()
        
        # Get info
        info = self.client.mdaController.get_mda_sequence_info(sequence)
        print("Sequence info:")
        print(f"  Total events: {info.get('total_events', 'N/A')}")
        print(f"  Estimated duration: {info.get('estimated_duration_minutes', 0):.1f} minutes")
        print()
        
        print("To execute:")
        print("  result = self.client.mdaController.run_native_mda_sequence(sequence)")
        print()


def main():
    parser = argparse.ArgumentParser(
        description="MDA Integration Demo for ImSwitch"
    )
    parser.add_argument(
        "--server",
        default="http://localhost:8001",
        help="ImSwitch server URL (default: http://localhost:8001)"
    )
    parser.add_argument(
        "--demo",
        choices=["simple", "timelapse", "full", "native", "all"],
        default="all",
        help="Which demo to run (default: all)"
    )
    
    args = parser.parse_args()
    
    demo = MDADemo(args.server)
    
    # Check if MDA is available
    print("=" * 70)
    print("Checking MDA capabilities...")
    print("=" * 70)
    caps = demo.check_capabilities()
    
    if not caps.get('mda_available'):
        print("❌ MDA functionality is not available")
        print("Make sure useq-schema is installed and ImSwitch is running")
        return
    
    print("✅ MDA functionality is available")
    print(f"  Available channels: {caps.get('available_channels', [])}")
    print(f"  Stage available: {caps.get('stage_available', False)}")
    print()
    
    # Run the selected demo
    if args.demo == 'simple' or args.demo == 'all':
        demo.demo_simple_zstack()
    
    if args.demo == 'timelapse' or args.demo == 'all':
        demo.demo_timelapse()
    
    if args.demo == 'full' or args.demo == 'all':
        demo.demo_full_mda()
    
    if args.demo == 'native' or args.demo == 'all':
        demo.demo_native_useq()
    
    print("=" * 70)
    print("Demo Complete")
    print("=" * 70)
    print()
    print("To actually run experiments, modify the scripts to call:")
    print("  demo.start_experiment(experiment)  # For dict-based experiments")
    print("  client.mdaController.run_native_mda_sequence(sequence)  # For useq objects")
    print()
    print("Make sure your ImSwitch setup is configured with appropriate hardware.")
    print()


if __name__ == "__main__":
    main()
