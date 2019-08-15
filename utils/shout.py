# Copyright © 2018–2019 lambda#0987
#
# CAPTAIN CAPSLOCK is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# CAPTAIN CAPSLOCK is distributed in the hope that it will be fun,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with CAPTAIN CAPSLOCK.  If not, see <https://www.gnu.org/licenses/>.

import functools
import itertools
import re
from pathlib import Path
from sys import maxunicode

# if the amount of shadowing builtins that i do bothers you, please fix your syntax highlighter / linter

def is_shout(str):
	words = [s for s in re.split(r'\b', str) if s and re.fullmatch(r'\w+', s)]
	stats = list(map(functools.partial(is_shout_word, len(words)), words))
	if not stats:
		return False  # prevent divide by zero
	return sum(stats) / len(stats) >= shout_coefficient(len(stats))

def is_shout_word(num_words, word, *, IGNORED_WORDS=frozenset({'I', 'OK'})):
	if word in IGNORED_WORDS:
		return False

	length = len(word)
	count = 0

	for c in word:
		if c in DEFAULT_IGNORABLE:
			length -= 1
		if c in UPPERCASE_LETTERS:
			count += 1

	return count / length >= (0.5 if num_words > 3 else 0.75)

def shout_coefficient(words: int):
	if words == 1:
		return 1.0
	if words == 2:
		return 0.5
	return min(words ** -2 + 0.40, 1)

properties_path = Path(__file__).parent.parent / 'data' / 'DerivedCoreProperties.txt'

def get_derived_core_properties():
	properties = {}

	with open(properties_path) as f:
		for property, range in parse_properties(f):
			properties.setdefault(property, set()).update(map(chr, range))

	return {property: frozenset(chars) for property, chars in properties.items()}

def get_derived_core_property(property):
	chars = set()
	desired = property

	with open(properties_path) as f:
		for property, range in parse_properties(f):
			if property == desired:
				chars.update(range)

	return frozenset(chars)

def parse_properties(f):
	for line in map(str.strip, f):
		if line.startswith('#') or not line:
			continue

		# ignore trailing comments too
		line = ''.join(itertools.takewhile(lambda c: c != '#', line))

		range, property = map(str.strip, line.split(';'))

		range = unicode_range_to_range(range)
		yield property, range

def unicode_range_to_range(range_str):
	return inclusive_range(*map(hex_to_int, range_str.split('..')))

hex_to_int = functools.partial(int, base=16)

def inclusive_range(start, stop=None, step=1):
	if stop is None:
		stop = start + 1
	else:
		stop += 1

	return range(start, start + 1 if stop is None else stop + 1, step)

UPPERCASE_LETTERS = frozenset(filter(str.isupper, map(chr, range(maxunicode + 1))))
DEFAULT_IGNORABLE = get_derived_core_property('Default_Ignorable_Code_Point')
