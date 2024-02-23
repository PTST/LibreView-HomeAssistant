[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/PTST/LibreView-HomeAssistant/graphs/commit-activity)
[![HACS Badge](https://img.shields.io/badge/HACS-Default-41BDF5.svg)](https://github.com/hacs/integration)
[![HACS Validation](https://github.com/PTST/LibreView-HomeAssistant/actions/workflows/HACS.yaml/badge.svg?branch=main)](https://github.com/ptst/LibreView-HomeAssistant/actions/workflows/HACS.yaml)
[![Hassfest Validation](https://github.com/PTST/LibreView-HomeAssistant/actions/workflows/Hassfest.yaml/badge.svg?branch=main)](https://github.com/ptst/LibreView-HomeAssistant/actions/workflows/Hassfest.yaml)

# LibreView Integration for Home Assistant

Will add a sensor per connected person showing their last reported blood glucose levels in either mmol/L or mg/dL  
Supports Home Assistant statistics  
![Screenshot 2024-02-23 083043](https://github.com/PTST/LibreView-HomeAssistant/assets/17211264/2112507b-bd45-4f4b-aace-f043eb0121c2)


## Installation
### HACS (Recommended)
1. Search HACS for the LibreView integration and install
2. Restart Home Assistant

### Manual
1. Using the tool of choice open the directory for your HA configuration (where you find `configuration.yaml`).
2. If you do not have a `custom_components` directory there, you need to create it.
3. In the `custom_components` directory create a new folder called `libreview`.
4. Place all files from the `custom_components/libreview/` directory in this repository.
6. Restart Home Assistant

## Setup
### LibreLinkUp
This integration uses the fact that you can share your data with other people using the LibreLinkUp app. Therefore you must first set this up.

1. Open your LibreLink App and click on the hamburger menu in the top left corner and click "Connected apps"  
![IMG_0621](https://github.com/PTST/LibreView-HomeAssistant/assets/17211264/875489d5-5883-4aa8-8900-9b3e10218aa2)

2. Click manage next to "LibreLinkUp"  
![IMG_0622](https://github.com/PTST/LibreView-HomeAssistant/assets/17211264/afb0302a-41fe-4b6b-b1b1-957bc610a354)

3. Click "Add connection"  
![IMG_0623](https://github.com/PTST/LibreView-HomeAssistant/assets/17211264/4a74bfb0-dc7d-4453-9a0f-ee741c74b419)

4. Enter a name and the email of the account you want to connect to.  
You can either use the same email as you LibreLink account, then you can just use the same login info later on  
or you can add a new email and use that later on to create a new user  
Then click "ADD"  
![IMG_0625](https://github.com/PTST/LibreView-HomeAssistant/assets/17211264/0f09456c-6966-4aed-bce0-6d6414e24f9e)

5. You should then get the following screen saying that an Invitation is pending    
![IMG_0626](https://github.com/PTST/LibreView-HomeAssistant/assets/17211264/2340558d-9f7d-4094-a2b7-00b9c2dd9b02)

6. Download and install the LibreLinkUp app on your phone from the [App Store](https://apps.apple.com/us/app/librelinkup/id1234323923) or the [Google Play Store](https://play.google.com/store/apps/details?id=org.nativescript.LibreLinkUp)

7.  Open the LibreLinkUp app you just installed.  
If in step 4 you used the same email as you did for your existing LibreView Account then click "Log in", and proceed to step 10.  Otherwise click the "Get started now" button, and then on the next screen click the "Create Account" button  
![IMG_0628](https://github.com/PTST/LibreView-HomeAssistant/assets/17211264/6741c45d-a556-4755-905c-56227083b7c4)

8. Accept the License Agreement and Privacy Policy

9. Create your new Account and make sure that you use the same email that you provided in step 4.  
![IMG_0634](https://github.com/PTST/LibreView-HomeAssistant/assets/17211264/a9ff1340-0923-4c23-8289-fbf261447ce3)

10. Then a prompt should appear shortly sating that xxx would like to share glucose information with you. Click Accept.  
Then proceed to Home Assistant for the setup of the integration there.  
![IMG_0641](https://github.com/PTST/LibreView-HomeAssistant/assets/17211264/2a666094-43c5-487b-9674-b7dd8d91e33f)


### Home Assistant

1. In Home Assistant click on Settings in the left-side navigation  
![IMG_0643](https://github.com/PTST/LibreView-HomeAssistant/assets/17211264/c55c490c-42d1-4688-bf93-272aad96193a)

2. Click on "Devices & Services"  
![IMG_0644](https://github.com/PTST/LibreView-HomeAssistant/assets/17211264/c6ddf8c7-9eaf-4ae0-bcba-c052651921ea)

3. Click on the "Add integration" button  
![IMG_0645](https://github.com/PTST/LibreView-HomeAssistant/assets/17211264/5abf79ee-3a30-46fe-a777-5612226dbf39)

4. Search for "LibreView" and click on the result  
![IMG_0646](https://github.com/PTST/LibreView-HomeAssistant/assets/17211264/f38dfede-46f4-49ff-abef-32048991f214)

5. Enter your login crendentials for the LibreLinkUp app and click Submit  
![IMG_0648](https://github.com/PTST/LibreView-HomeAssistant/assets/17211264/720cb5ea-e195-4a52-89c1-50bc2fa7a7d4)

6. Select your preferred unit of measurement and click submit  
![IMG_0649](https://github.com/PTST/LibreView-HomeAssistant/assets/17211264/002eee8d-f50c-44fe-8717-83cbb3e256c8)

7. Click finish  
![IMG_0650](https://github.com/PTST/LibreView-HomeAssistant/assets/17211264/78e46354-af44-483a-aa03-5e7eb3fad2d2)

8. You now have a new sensor for each person who shares their glucose measurements with you.  
![IMG_0651](https://github.com/PTST/LibreView-HomeAssistant/assets/17211264/b7dcfcf5-0c62-4027-a9a9-07f04624a540)
