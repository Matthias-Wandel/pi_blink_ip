# Blink IP address on headless Raspberry Pi
On YouTube: https://youtube.com/embed/XbJ5vT8FvXU

I often have this problem.  I have a headless (no monitor or keyboard) Raspberry Pi,
put a flash card in already configured for my network (using another Raspberry Pi), 
and it connects to my network.  But I don't what IP address my DHCP server assigned to it,
so I can't connect to it via SSH.

I can look on my router to see what address was just assigned, but that's awkward and not practical
if it's on someone else's Wi-Fi network.

So I wrote this Python script which blinks the last digits of the IP address on the built-in status LED
of a Raspberry Pi after boot up.  But rather than using Morse code (too complicated), I blink it out
the digits as roman numerals, with 'I' (1) being a short blink, 'V' (5) being a medium long blink
and 'X' (10) as a long blink. I use X to represent the digit zero.  That way I don't have to try to
count 8 or 9 blinks sometimes.

Each decimal digit is blinked separately, so 102 is blinked as I X II,  not CII

If the second last octet of the IP4 address is a zero (which it usually is), it is omitted.

So if my Pi is assigned 192.168.0.249, it will only blink "249".

If it were assigned, 10.10.5.0, it would blink '5' and '0'.

If there is no IP address, it blinks "000"

Sometimes Wi-Fi will initialize with a bogus IP address but not connect, in which case, you may recognize
that the last two octets blinked out don't match your network at all.

*Example blink patterns:*

<table border=1 cellspacing=0 cellpadding=5>
<tr><th>IP4 address<th>Digits blinked<th>Roman digits<th>Blink pattern
<tr><td>192.168.0.105<td><center>105<td><center>I X V<td>
    <center><b>&bull; &nbsp; &mdash; &nbsp; &bull; -</b>
<tr><td>192.168.2.349<td><center>2 349<td><center>II &nbsp; III IV IX<td>
    <center><b>&bull; &bull; &nbsp; &nbsp; &nbsp; &bull; &bull; &bull; &nbsp; &bull; - &nbsp; &bull; &mdash;</b>
<tr><td>10.10.456.789<td><center>456 789<td><center>IV V VI &nbsp; VII VIII IX<td>
    <center><b>&bull; - &nbsp; - &nbsp; - &bull;
    &nbsp; &nbsp; &nbsp;
    - &bull; &bull; &nbsp;  - &bull; &bull; &bull; &nbsp; &bull; &mdash;</b>
<tr><td>None (just 127.0.0.1)<td><center>000<td><center>X X X<td>
    <center><b>&mdash; &nbsp; &mdash; &nbsp; &mdash;</b>

</table>

Short blinks (I) are 0.1 seconds long  
Medium blinks (V) are 0.4 seconds long  
Long blinks (X) are 1.2 seconds long.  
Time between digits is 1 second.  
Time between octets is 2 seconds.

The IP address is blinked after boot completes, waiting for Wi-Fi to initialize.  The IP address is blinked
ten times, with a three second pause between.  After that the status LED is returned to its default
functionality, to blink on flash card access.
On Raspbery Pi zero W, there is only one green LED used for power and status, so it blinks that one.
On other Pi's, it blinks the green status LED.

The script needs to run as root.  If you run it, it will check hat it has an IP which isn't changing,
then blinks the IP address.  There is also an "install" option to add it to root's crontab
to make it run at startup.

To set it up to run at boot, from the directory that you put blink_ip.py into, just run:

```
sudo ./blink_ip.py install
```

You can get this this script from github here:

https://github.com/Matthias-Wandel/pi_blink_ip

Or by typing `git clone https://github.com/Matthias-Wandel/blink_ip`

or via this link: http://woodgears.ca/tech/blink_ip.py

One dependency needs to be installed on the raspberry py:

```
sudo pip install --user python-crontab
```

This isn't the first program written to do this, but I couldn't find one that I thought
was useful.  The solutions I found would blink every digit of the whole address (too hard to decode),
blink numbers like '9' with Morse code or nine blinks (too hard to count), use an external
LED instead of status LED (too inconvenient), and weren't set up to figure out the IP address
at startup, and so on.  So I wrote this one to be the best IP address blinker there is!
