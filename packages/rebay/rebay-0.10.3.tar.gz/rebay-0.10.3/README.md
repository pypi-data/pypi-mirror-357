# rebay

Scrape an ebay shop's inventory into a Reverb compatible format.

## Installation

Requires Python 3.10 <= version < 3.12.

Install with:

Clone this repository and open it in a shell.<br>
Then use the command:
(mac)
<pre>
pip3 install .
</pre>
(windows/linux)
<pre>
pip install .
</pre>

Alternatively, if you have [Git](https://git-scm.com/) and [Github CLI](https://cli.github.com/) installed and authenticated,
you should be able to install with:<br>
(mac)
<pre>
pip3 install git+https://github.com/matt-manes/rebay
</pre>
(windows/linux)
<pre>
pip install git+https://github.com/matt-manes/rebay
</pre>


## Usage
This package will be installed as a script,
so you don't need to have any particular folder open in terminal to run it.<br>
I'd suggest running it from the same location everytime though so that you only have one set of output and log folders.<br>

To run in terminal:
<pre>
>rebay shopname
</pre>
To see tool help, type `rebay -h`:
<pre>
>rebay -h
usage: rebay [-h] [-t MAX_THREADS] shop_name

positional arguments:
  shop_name             The name of the shop to scrape.

options:
  -h, --help            show this help message and exit
  -t MAX_THREADS, --max_threads MAX_THREADS
                        Max number of threads to use. Default is 5. Too many and they'll error page you.
</pre>
