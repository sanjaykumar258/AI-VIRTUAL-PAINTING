
# GesturePainter

This Python mini project utilizes OpenCV, Numpy, and MediaPipe to create a virtual painting application that allows you to draw on the screen using hand gestures.

## Overview

This virtual painting application recognizes hand gestures captured by your webcam and maps them to different actions, such as changing colors or clearing the canvas. The script uses hand landmarks predicted by MediaPipe to track the position of your hand and fingers in real-time.

## Features

- **Color Options:** Choose from four different colors - blue, green, red, and yellow.
- **Clear Option:** Clear the canvas with a hand gesture to start fresh.
- **Real-time Drawing:** Experience real-time drawing on the screen based on your hand movements.

## Prerequisites

Before running the script, ensure you have the following installed:

- Python
- OpenCV
- NumPy
- MediaPipe

Install the required packages using:

```bash
pip install opencv-python numpy mediapipe
```

## Usage

1. Clone the repository:

```bash
git clone https://github.com/sahilmate/GesturePainter.git
cd GesturePainter
```

2. Run the script:

```bash
python main.py
```

3. Interact with the virtual canvas using your hand gestures. Press 'q' key in order to end the process.

## Contributing

We welcome contributions to enhance the functionality and features of this project. If you'd like to contribute, please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature: `git checkout -b feature-new-feature`
3. Commit your changes: `git commit -m 'Add new feature'`
4. Push to the branch: `git push origin feature-new-feature`
5. Open a pull request.

## Future Enhancements

Here are some ideas for future enhancements:

- Ability to save the drawn images
- Support for additional hand gestures and actions.
- Improvements to the user interface and canvas.
- Multi-hand support for collaborative drawing.

Feel free to suggest new features and improvements or contribute to the existing ones!

## License

This project is licensed under the [MIT License](LICENSE).

```
Happy drawing! 🎨
```
