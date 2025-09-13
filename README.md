# Morse_Blink_Translator
This is a Morse Blink Translator project in which we can convert our blink sequences into dots and dashes and therefore we can convert them into morse code ad communicate.


Blink Less than 0.3 seconds - "." ;
Blink Less than 1 seconds - "-" ;
Blink Greater than or equal to 1.5 seconds - " " (Space For New Word) ;
We are using OpenCV and mediapipe for this project.
IT WORKS BY USING THE EAR(EYE ASPECT RATIO) CONCEPT WHICH USES THE 6 LANDMARKS AROUND THE EYE TO DETECT A BLINK.WE ARE ONLY DETECTING THE RIGHT EYE BECAUSE ONE EYE IS ENOUGH TO DETECT A BLINK.
