# lbptoolspy-lite

This is similar to the normal lbptoolspy but some functions are missing to ensure this will work in any python environment, like in android

## The missing functions are

`install_mods_to_bigfart` <br />
`lbpfile2json` <br />
`json2lbpfile` <br />

## Other differences
Because ImageMagick is not used, the `image2tex` function will produce .tex files with messed up colours and overall a inaccurate image, this is because Pillow does not support dtx5 compression to conversions