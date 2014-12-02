

class Growl:
    _objc_ = None

    @staticmethod
    def __notify__(title, *subtitle):
        subtitle = None if len(subtitle) == 0 else subtitle[0]

        global _objc_
        def swizzle(cls, SEL, func):
            old_IMP = cls.instanceMethodForSelector_(SEL)
            def wrapper(self, *args, **kwargs):
                return func(self, old_IMP, *args, **kwargs)
            new_IMP = _objc_.selector(wrapper, selector=old_IMP.selector, signature=old_IMP.signature)
            _objc_.classAddMethod(cls, SEL, new_IMP)

        def swizzled_bundleIdentifier(self, original):
            """Swizzle [NSBundle bundleIdentifier] to make NSUserNotifications
            work.

            To post NSUserNotifications OS X requires the binary to be packaged
            as an application bundle. To circumvent this restriction, we modify
            `bundleIdentifier` to return a fake bundle identifier.

            Original idea for this approach by Norio Numura:
                https://github.com/norio-nomura/usernotification
            """
            return 'com.apple.terminal'


        if not Growl._objc_:
            try:
                _objc_ = __import__("objc")
                Growl._objc_ = _objc_
                swizzle(
                    _objc_.lookUpClass('NSBundle'),
                    b'bundleIdentifier',
                    swizzled_bundleIdentifier
                )
            except:
                print "The objc module is not supported on this system."
                return

        NSUserNotification = _objc_.lookUpClass('NSUserNotification')
        NSUserNotificationCenter = _objc_.lookUpClass('NSUserNotificationCenter')
        if not NSUserNotification or not NSUserNotificationCenter:
            print('NSUserNotifcation is not supported by your version of Mac OS X')
            return

        notification = NSUserNotification.alloc().init()
        notification.setTitle_(str(title))
        if subtitle is not None:
            notification.setSubtitle_(str(subtitle))

        notification_center = NSUserNotificationCenter.defaultUserNotificationCenter()
        notification_center.deliverNotification_(notification)

    @staticmethod
    def notify(*message):
        title = message[0] if len(message) > 0 else ""
        if len(message) > 1:
            message = " ".join(list(message)[1:])
        else:
            title, message = "Alert", title

        Growl.__notify__(title, message)



def notify(*message):
    Growl.notify(*message)

