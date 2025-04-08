# Mixxx AI DJ Copilot Extension

## Overview

The Mixxx AI DJ Copilot is an intelligent extension for DJ software that learns and replicates a user's unique mixing style. Acting as a collaborative partner rather than a replacement, this extension analyzes your DJing habits, recommends tracks, suggests mixing techniques, and can eventually generate complete DJ sets that match your personal style.

## Key Features

- **Style Learning**: Captures and analyzes your unique DJ style, including effects usage, bass swaps, chops, blending techniques, energy building, and music preferences
- **Smart Recommendations**: Suggests tracks from your existing library that flow well with your current set
- **External Discovery**: Integrates with SoundCloud API to recommend new tracks similar to your style
- **Mixing Techniques**: Learns when and how you apply effects, helping recreate your signature sound
- **Full Set Generation**: Creates complete DJ sets in your style (advanced feature)
- **User-Configurable**: Disable automatic features like chops, effects, or beatmatching to maintain your preferred level of control

## Development Approach

### Platform Selection

We're starting with Mixxx, an open-source DJ software, due to its extensibility and scripting capabilities. While the ultimate goal includes supporting commercial platforms like Rekordbox and Serato, their closed ecosystems make initial development challenging. Our plan is to develop a robust prototype on Mixxx, then approach Pioneer with demonstrated value for potential Rekordbox integration.

### Technical Implementation

The extension takes a modular approach with these key components:

1. **Data Capture**: Uses Mixxx's MIDI scripting to log detailed mixing actions, track selections, and effect applications
2. **Style Analysis**: Processes captured data to identify patterns in your mixing style
3. **Recommendation Engine**: Suggests appropriate tracks based on learned preferences
4. **DJ Style Replication**: Applies machine learning to recreate mixing techniques specific to your style
5. **User Interface**: Provides intuitive controls to configure the extension's behavior

### Project Status

This project is currently in the initial development phase. We're focused on:
- Setting up the core architecture
- Developing data capture mechanisms through Mixxx scripting
- Creating foundational database structures for logging user actions
- Planning integration with SoundCloud's API for external track recommendations

## Installation

*Detailed installation instructions will be added as the project matures*

### Prerequisites
- Mixxx (version 2.3 or later)
- Python 3.8+
- Required Python packages (see requirements.txt)

### Quick Start

1. Clone this repository
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the setup script:
   ```
   python scripts/setup_database.py
   ```
4. Install the Mixxx scripts:
   ```
   python scripts/install_mixxx_scripts.py
   ```

## Project Structure

```
mixxx-ai-copilot/
├── config/                 # Configuration files
├── src/                    # Source code
│   ├── data_capture/       # MIDI scripting and action logging
│   ├── data_storage/       # Database models and management
│   ├── analysis/           # Style analysis and pattern recognition
│   ├── recommendation/     # Track recommendation engine
│   ├── external_api/       # Integration with SoundCloud API
│   ├── dj_generator/       # DJ set generation
│   ├── ui/                 # User interface components
│   └── utils/              # Utility functions
├── tests/                  # Test suite
├── docs/                   # Documentation
└── scripts/                # Utility scripts
```

## Future Steps

1. **Testing and Iteration**: Gather feedback from real DJs to refine the algorithms
2. **Feature Expansion**: Gradually add more sophisticated style learning capabilities
3. **Platform Integration**: Once mature, approach Pioneer for potential Rekordbox integration
4. **Community Building**: Engage with the DJ community to ensure the tool enhances rather than replaces DJ skills

## Contribution

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

- The Mixxx development team for creating an excellent open-source DJ platform
- SoundCloud for their API that enables music discovery
- All DJs who provide feedback and help shape this tool