# coding: utf8

from ditto.validation.converter import converter
import argparse
import traceback


def main():
	'''Run all requested test scripts in the validation/scripts folder.

- "-f" (for feeders) used to specify feeders
- "-b" (for before) used to specify from formats
- "-a" (for after) used to specify to formats

**Usage:**

Run the OpenDSS--->DiTTo--->CYME conversion on the 13 node feeder:

$ python parse.py -f ieee_13_node -b opendss -a cyme

More combinations:

$ python parse.py -f ieee_13_node -f ieee_123_node -b opendss -b cyme -a opendss -a gridlabd

Run all feeder and all possible combinations:

$ python parse.py

.. note:: For now, "success" means that the conversion did not crash, not that we get a working feeder at the end...

author: Nicolas Gensollen. October 2017.

'''
	#Parse the arguments
	parser=argparse.ArgumentParser()

	#Feeder list
	parser.add_argument('-f', action='append', dest='feeder_list', default=[])

	#Format from
	parser.add_argument('-b', action='append', dest='format_from', default=[])

	#Format to
	parser.add_argument('-a', action='append', dest='format_to', default=[])

	results=parser.parse_args()

	#If nothing is provided, run everything...
	if results.feeder_list==[]:
		feeder_list=['ieee_13_node', 'ieee_123_node']
	else:
		feeder_list=results.feeder_list

	if results.format_from==[]:
		format_from=['opendss', 'cyme', 'gridlabd']
	else:
		format_from=results.format_from

	if results.format_to==[]:
		format_to=['opendss', 'cyme', 'gridlabd']
	else:
		format_to=results.format_to

	#Store failures and success for end summary
	failures=[]
	success=[]

	for _from in format_from:
		for _to in format_to:

			print('>>>-- FROM: {}'.format(_from))
			print('>>>-- TO: {}'.format(_to))

			_converter=converter(feeder_list, _from, _to)

			try:
				_converter.convert()
				print('SUCCESS..!!')
				success.append('{fromm}_to_{too}'.format(fromm=_from, too=_to))
			except:
				print('FAIL..!!')
				failures.append('{fromm}_to_{too}'.format(fromm=_from, too=_to))
				traceback.print_exc()
				pass


	#Print summary of success and failures
	print('='*60)
	print('Success :')
	for s in success: print(s)
	print('='*60)
	print('Failures :')
	for s in failures: print(s)
	print('='*60)


if __name__ == '__main__':
	main()
