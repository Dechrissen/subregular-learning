# subreglib

This directory contains the `.plebby` files for use with `plebby` which is included in [The Language Toolkit](https://github.com/vvulpes0/Language-Toolkit-2) by Dakotah Lambert.  

## `.plebby` files

Currently, these files uses three varying alphabet sizes (4, 16, 64) and three different *k*-values (2, 4, 8). For the majority of language types, there is one `.plebby` file per alphabet size / *k*-value configuration (9) plus 3 more for the Star-free and Regular languages with the 3 different alphabet sizes. There are 12 total `.plebby` files. They are named according to the scheme `subreglib_k<value>_alph<size>.plebby`, or in the case of the Star-free and Regular files, `subreglib_SFR_alph<size>.plebby`..  

Each of these files can be used with `plebby` to generate the `.att` files for each language (some of which already exist in `/src/fstlib/att_format`).  

*Note*: The file `subreglib_k8_alph4.plebby` is the one exception, given that its *k*-value is greater than its alphabet size. The workaround for this case was to repeat alphabet symbols to create long enough *k*-factors, like below. 

```
=abcdabcd  </a /b /c /d /a /b /c /d>
```

This is different from how it would be done in a file where enough alphabet symbols exist, as in `subreglib_k8_alph16.plebby`, where we can do:

```
=abcdefgh  </a /b /c /d /e /f /g /h>
```

## `ins.txt` and `outs.txt`

These two files also exist in the directory, and they contain a mapping of all 64 possible alphabet symbols to their UTF-8 values, for use with [openfst](http://www.openfst.org/twiki/bin/view/FST/WebHome) and `pynini` for creating FSTs. These won't need to be changed unless a greater max alphabet size is desired for use in the `.plebby` files. In this case, refer to the 'Data generation' section in this project's main README to learn about editing these files, and/or the script `/src/fstlib/att_format/make-ins-and-outs.py` which can be edited to support more than 64 symbols. In any case, the pair of these files (`ins.txt` / `outs.txt`) needs to be placed in both *this* directory and the `/src/fstlib/att_format` directory if updated.