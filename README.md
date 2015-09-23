# pupil-support

Class Pupil eye tracker integration. Mainly for saccad detection (useful for fixation) and logging.
The main idea is that if a saccade is done during fixation period, subject was not fixating. Velocity thresold can be costumized.

1) Install pupil_capture bundle from pupil labs. Run it.

2) git clone https://github.com/patra/pupil-support 

3) python pupil_support.py should do something.


Typical usage:

	# log for 10 seconds and detect saccades for 2 secconds
	pupil = Pupil()
	p = pupil.test_pupil()

	ti = time()
	tf = time()
	if p:
		pupil.record_start()
		pupil.detect_sacc_start()
		while tf-ti < 10:
			if tf-i>2:
				pupil.detect_sacc_stop()
			tf = time()

		pupil.record_stop()
