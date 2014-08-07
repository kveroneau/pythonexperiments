Lock and unlock your Linux desktop using your Android smartphone!
Unlike BlueProximity, this won't use up valuable power on your smartphone.
You run it when you want to specifically lock or unlock your desktop or laptop.
It works over a bluetooth connection, so your smartphone does not need to be on the same
network as your PC.  This is also a great base project to create your own bluetooth services
which android can connect to.

## Using:
First install SL4A on your android device, and copy the mylib.py from the android/ directory
in this repo.  Then load pc_locker.py onto your android phone.  Create a shortcut on your
homescreen for easy one-tap access to the script.  A demo video will be available soon.

After you will need to update the bluez_locker.py file with your devices bluetooth MAC addresses.
You can add as many devices as you want, but be warned that it does loop through each one, so only
add at most 3 devices.  I only have 2, my desktop, and my laptop.  This way, I can lock and unlock
both at the very same time with a single touch of a button.

Next on your PC, tailor the "screens-lock" and "screens-unlock" to your specific desktop
environment, so that they start the screensaver, and stops the screensaver.  The same
code from BlueProximity can be used in these 2 scripts.  Then run bluez_locker.py.
You can use the '-d' option to daemonize it.
