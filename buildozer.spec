[app]

title = Private Gallery
package.name = privategallery
package.domain = org.private

source.dir = .
source.include_exts = py,kv,png,jpg,jpeg,ttf

version = 0.1

requirements = python3,kivy,plyer,cryptography,pyjnius
android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,USE_FINGERPRINT

orientation = portrait
fullscreen = 0
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True

[buildozer]

log_level = 2
warn_on_root = 1
