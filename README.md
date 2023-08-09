**

## Splunk Vetting Python App

** 

**Porpuse:**

The normal script used for vetting works well, however it has some known issues, that if you are not aware of them, it could delay a lot of an engagement, an example of this is metadata files issue, the normal script deletes everything inside default and local, so this could be a problem for a customer. 
This script is an improved version, this fixes those known issues and I added some other features like the bulk mode, delete temporal files generate by script, classification of Vetted apps and non-vetted apps, and Quick Fixes.

The new version is planned to be installed as an app for MacOS or Linux, this script works with some other scripts to make all the job properly.

**What's new in this Python App:**

The new Python App for Cloud Vetting has the following new features:

**Bulk Mode:**

 - This mode allows you to run vetting in bulk mode, so all apps in the
   same folder will be vetted automatically, at the end, if an app is
   successfully vetted, it is moved to the Vetted folder, if it fails,
   moves the html report to a folder called “Apps With Issues” in Vetted
   folder and deletes all temporal files created.

**Analysis of Vetted and Non-Vetted apps:**

 - This script analyses each app if they passed the Vetting or Not

**Classification and delete temporal files generate by script:**

 - Depending on the results of the preview script, this will be running
   a Classification of apps and clean all temporal files and creating
   the reports to the “Apps With Issues” folder.

**Quick Fixes:**

 - Script that will be running some fixes to the most common issues when
   vetting apps, like permissions, dashboard versions, old features
   etc.…

**Instructions for Installation:**

Requirements:
 -Splunk Enterprise must be installed in the Machine.
 -Python 3 is required

Using the pip tool install the package:
 - pip install vetting_app-0.1.0.tar.gz
   The **vetting_app-0.1.0.tar.gz** can be found in the dist folder.

**Usage**

    usage: svta [-h] [--bulk] [--app APP] [-l] [-p] [-d] [-b] [--configure]

    options:
      -h, --help            Show this help message and exit
      --bulk                Run vettings in bulk mode
      --app APP             Run vetting for a specific app
      -l, --use_local_only  Vetting for Local Only
      -p, --use_private_app
                            Vetting Private Apps
      -d, --ignore_local    Vetting and Ignoring Local
      -b, --bin_delete      Vetting and bin Delete
      --configure           Configure the SVTA App


**The first time you run the command, it will start the asking the required details for the App configuration**
