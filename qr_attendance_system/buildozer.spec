[app]

# Application title
title = QR Attendance System

# Package name
package.name = qrattendance

# Package domain
package.domain = org.qrattendance

# Source code directory
source.dir = .

# Source files to include
source.include_exts = py,png,jpg,kv,atlas,json

# Application versioning
version = 1.0.0

# Requirements
requirements = python3,kivy==2.3.0,kivymd==1.1.1,requests,qrcode,pillow,pyzbar,android,pyjnius,plyer

# Supported orientations
orientation = portrait

# Fullscreen mode
fullscreen = 0

# Presplash background color
presplash.color = #667eea

# Android specific settings
[app:android]

# Minimum API level
android.api = 31

# Target API level (Android 12+)
android.minapi = 21

# Android NDK version
android.ndk = 25b

# Android SDK version
android.sdk = 33

# Permissions
android.permissions = INTERNET,CAMERA,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# Application icon
#icon.filename = %(source.dir)s/data/icon.png

# Presplash image
#presplash.filename = %(source.dir)s/data/presplash.png

# Android entry point
android.entrypoint = org.kivy.android.PythonActivity

# Enable AndroidX support
android.enable_androidx = True

# Gradle dependencies
android.gradle_dependencies = com.google.zxing:core:3.5.0

# Architecture to build for
android.archs = arm64-v8a,armeabi-v7a

[buildozer]

# Log level (0 = error only, 1 = info, 2 = debug)
log_level = 2

# Display warning if buildozer is run as root
warn_on_root = 1

# Build directory
build_dir = ./.buildozer

# Binary directory
bin_dir = ./bin
