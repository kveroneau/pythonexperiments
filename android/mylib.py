import android

droid = android.Android()

def getChoice(items):
  droid.dialogCreateAlert('Select one:')
  droid.dialogSetItems(items)
  droid.dialogShow()
  result = droid.dialogGetResponse().result
  droid.dialogDismiss()
  return items[result['item']]

def alert(msg, btn1, btn2):
  droid.dialogCreateAlert(APP_TITLE, msg)
  droid.dialogSetPositiveButtonText(btn1)
  droid.dialogSetNegativeButtonText(btn2)
  droid.dialogShow()
  result = droid.dialogGetResponse().result
  droid.dialogDismiss()
  if result['which'] == 'positive':
    return True
  return False

def getNumber(prompt, btn_text):
  droid.dialogCreateInput(APP_TITLE, prompt, '', 'number')
  droid.dialogSetPositiveButtonText(btn_text)
  droid.dialogShow()
  data = droid.dialogGetResponse().result['value']
  droid.dialogDismiss()
  return int(data)
