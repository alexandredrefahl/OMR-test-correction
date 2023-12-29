# OMR CLI Test Correction (2019)

This is a **Command Line Interface written in python to automatic correct test** and report generator.

Using computer vision techniques and Python's OpenCV library, the system digitizes physical paper tests and recognizes the options marked by the student and corrects them according to a pre-informed answer sheet.

The system **generates a new image with the corrected test** indicating to the student which would have been the correct option by marking it in red, or confirming the choice of the correct option with a green circle. At the end, it informs the percentage of correct answers. (the grade)

Furthermore, for the teacher, he also prepares statistics on the most correct/wrong questions, and which contents are most efficient/deficient for the group of students based on the individual questions. 

It uses : Python, OpenCV, SQLLite

### Test with answer sheet marked by the student

![image](https://github.com/alexandredrefahl/OCR-test-correction/assets/24326296/0042f7e9-d489-4a93-b8b4-6456a9671518)

Student identification is done by marking the registration number and the options marked below.

### Automatic Corrected Test

The system then processes the image, marks the option that should have been chosen in red, and the option correctly marked in green and calculates the total score by marking it in the test on the side (in 
this case 22.5% of correct answers)

![image](https://github.com/alexandredrefahl/OCR-test-correction/assets/24326296/84f9640b-b986-4524-b710-c57e6010e5dc)


