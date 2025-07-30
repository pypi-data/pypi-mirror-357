# sage_setup: distribution = sagemath-categories
"multi_replace"


# start delvewheel patch
def _delvewheel_patch_1_10_1():
    import os
    if os.path.isdir(libs_dir := os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'passagemath_categories.libs'))):
        os.add_dll_directory(libs_dir)


_delvewheel_patch_1_10_1()
del _delvewheel_patch_1_10_1
# end delvewheel patch

##########################################################################
#
# multi_replace function
#
# By Xavier Defrang.
#
# From the Python cookbook:
#
#  http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/81330
#
##########################################################################


import re


#
# The simplest, lambda-based implementation
#

def multiple_replace(dic, text):
    """
    Replace in 'text' all occurrences of any key in the given
    dictionary by its corresponding value.  Returns the new string.

    EXAMPLES::

        sage: from sage.misc.multireplace import multiple_replace
        sage: txt = "This monkey really likes the bananas."
        sage: dic = {'monkey': 'penguin', 'bananas': 'fish'}
        sage: multiple_replace(dic, txt)
        'This penguin really likes the fish.'
    """
    # Create a regular expression  from the dictionary keys
    regex = re.compile("(%s)" % "|".join(re.escape(k) for k in dic))

    # For each match, look-up corresponding value in dictionary
    return regex.sub(lambda mo: dic[mo.string[mo.start():mo.end()]], text)