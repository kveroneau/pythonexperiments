import android

droid = android.Android()
print "Turning bluetooth radio on..."
droid.toggleBluetoothState(True)
print "Waiting for bluetooth connection..."
droid.bluetoothAccept()
fname = droid.bluetoothReadLine().result
print "Receiving %s..." % fname
flen = int(droid.bluetoothReadLine().result)
open('scripts/%s' % fname, 'w').write(droid.bluetoothRead(flen).result)
print "Saved %s bytes." % flen
droid.bluetoothStop()
