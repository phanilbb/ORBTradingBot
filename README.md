# ORBTradingBot

**Project setup**

1. Install Python 3.7 
    ```brew install python@3.7```
2. Create virtual environment
    ```python3.7 -m venv venv```
3. Activate virtual environment
     ```source venv/bin/activate```
4. Install the requirements
    ```pip install -r requirements.txt```



**Setting up AWS Keys**

You can set the AWS Access Key ID and Secret Access Key in PyCharm by configuring the environment variables in the Run Configuration.

Here's how you can do it:

1. Open your PyCharm project and navigate to the Run Configuration you want to modify. You can access the Run Configuration by clicking on the drop-down arrow next to the Run button in the toolbar and selecting "Edit Configurations...".

2. In the Run Configuration window, click on the "Environment" tab.

3. Click on the "..." button next to the "Environment variables" field to open the Environment Variables dialog.

4. Add two environment variables with the following names and values:

    ```AWS_ACCESS_KEY_ID = your_access_key_id```
    ```AWS_SECRET_ACCESS_KEY = your_secret_access_key```
5. Replace your_access_key_id and your_secret_access_key with your own Access Key ID and Secret Access Key.
6. Click "OK" to close the Environment Variables dialog.
7. Click "OK" again to save the Run Configuration.

