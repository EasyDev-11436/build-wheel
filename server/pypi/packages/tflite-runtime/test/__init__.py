from os.path import dirname, join
import unittest


class TestTfliteRuntime(unittest.TestCase):

    # See https://www.tensorflow.org/lite/performance/post_training_integer_quant and
    # https://www.tensorflow.org/lite/guide/python .
    def test_mnist(self):
        import numpy as np
        import tflite_runtime.interpreter as tflite

        test_dir = dirname(__file__)

        # The model file was generated by generate.py.
        interpreter = tflite.Interpreter(model_path=join(test_dir, "mnist.tflite"))
        interpreter.allocate_tensors()
        input_details = interpreter.get_input_details()[0]
        output_details = interpreter.get_output_details()[0]

        # The test file was generated as follows:
        #   >>> (x_train, y_train), (x_test, y_test) = tf.keras.datasets.mnist.load_data()
        #   >>> np.save("test.npy", x_test[:5])
        #
        # To see these images:
        #   >>> np.set_printoptions(linewidth=150)
        #   >>> x_test[0] etc.
        test_images = np.load(join(test_dir, "test.npy"))

        # In the third sample, the model incorrectly outputs a slanted 1 as 8.
        expected = [7, 2, 8, 0, 4]

        for i, test_image in enumerate(test_images):
            test_image = np.expand_dims(test_image, axis=0).astype(input_details["dtype"])
            interpreter.set_tensor(input_details["index"], test_image)
            interpreter.invoke()
            output = interpreter.get_tensor(output_details["index"])[0]
            self.assertEqual(expected[i], output.argmax())
