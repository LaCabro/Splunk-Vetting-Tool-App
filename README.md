**

## Splunk Vetting Python App

** 

The Splunk Vetting Tool App is a python app that helps users to vet apps for Splunk Cloud. It checks the compatibility, security, and performance of the apps and provides a report with the results. The app is designed to work with python 3 and can be installed with pip.

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

**Installation instructions:**

- Make sure you have **python 3** installed on your system. You can check the version by running **"python –version"** in a terminal or command prompt.
- Install pip, the python package manager, if you don't have it already. You can follow the instructions [[here]](https://pip.pypa.io/en/stable/installation/) to install pip.
- Install the Splunk Vetting Tool App by running **"pip install vetting\_app-1.0.0.tar.gz"** in a terminal or command prompt. This will download and install the app and its dependencies.
- To run the app, navigate to the directory where you installed it and run **"python -m vetting-app"**. This will launch the app's user interface, where you can select the apps, you want to vet and start the process.
- To uninstall the app, run **"pip uninstall vetting-app"** in a terminal or command prompt.

**Usage instructions:**

The svta command is used to run the Splunk Vetting Tool App from a terminal or command prompt. It accepts various options to customize the vetting process and the app behavior.

Options:

- To see the help message and a list of all the available options, run "svta -h" or **"svta –help".**
- To run vettings in bulk mode, which means vetting all the apps in the apps directory, use the --bulk option. For example, **"svta --bulk".**
- To run vetting for a specific app, use the --app option followed by the app name. For example, **"svta --app=my\_app".**
- To vet only the local files of the apps, use the -l or --use\_local\_only option. This will ignore any files that are not in the local directory of the app. For example, **"svta --app=my\_app -l"** or **"svta –bulk -l".**
- To vet private apps, which are apps that are not published on Splunkbase, use the -p or --use\_private\_app option. This will skip some checks that are only applicable to public apps. For example, **"svta --app=my\_app -p"** or **"svta –bulk -p".**
- To vet the apps and ignore any local files, use the -d or --ignore\_local option. This will exclude any files that are in the local directory of the app from the vetting process. For example, **"svta --app=my\_app -d"** or **"svta –bulk -d".**
- To vet the apps and delete any files that are in the bin directory of the app, use the -b or --bin\_delete option. This will remove any executable files that are not allowed in Splunk Cloud. For example, **"svta --app=my\_app -b"** or **"svta –bulk -b".**
- To configure the SVTA App, such as setting up the credentials, directories, and preferences, use the --configure option. This will launch a configuration wizard that will guide you through the steps. For example, **"svta –configure".**
  - This configuration wizard is executed automatically the first time you run the script, however if you require to update any information related with your credentials or Splunk path, then you can run the configuration wizard manually with option described before.
- To run QuickFix on the apps you want to run vetting, use the --fix option. This will automatically fix some common issues that can be detected and resolved by the app. For example, **"svta –fix".**
  - Included fixes:
    - Earliest and lasts time parameters updater.
    - Dashboards Version
    - Adding sc-admin role to metadata files
    - Updating user permissions of KO
      
           _ **More Fixes will be added in a future release. If you have any questions or recommendations, please send an email to ccarvajal@bitsioinc.com** _

You can combine multiple options to customize your vetting process. For example, if you want to run vetting for a private app and delete any bin files, you can run "svta --app my\_private\_app -p -b."
