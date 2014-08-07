import android, mylib

droid = android.Android()

mylib.APP_TITLE = 'PC Locker'
DEVICE_LIST = ['00:00:00:00:00:00', '00:00:00:00:00:00']

data = 'LOCK' if mylib.alert('Lock or Unlock?', 'Lock', 'Unlock') else 'UNLOCK'

print "Turning bluetooth radio on..."
droid.toggleBluetoothState(True)
for device in DEVICE_LIST:
    print "Connecting to PC..."
    result = droid.bluetoothConnect('457807c0-4897-11df-9879-0800200c9a66',device).result
    if result is None:
        droid.makeToast('Unable to connect to %s' % device)
        continue
    print "Connected.  Sending data..."
    droid.bluetoothWrite(data)
    msg = droid.bluetoothReadLine().result
    droid.notify('PC Locker', msg)
    print "Disconnected."
    droid.bluetoothStop()
