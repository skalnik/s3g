#!/usr/bin/python
 
import unittest2 as unittest
 
if __name__ == "__main__":
    all_tests = unittest.TestLoader().discover('tests', pattern='*.py')
    unittest.TextTestRunner().run(all_tests)