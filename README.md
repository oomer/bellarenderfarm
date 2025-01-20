## Oversimplified setup of a tiny Windows Bella renderfarm 

> THIS code is no longer developed but will remain for educational purposes. All future work will occur in the Linux based installers at https://github.com/oomer/oomerfarm

***Deadline*** is free-to-use software to create a renderfarm. It has 20 years of features and security wrappers ideal for the biggest of studios. This guide basically ignores most of those features and security wrappers to help a lone artist set up a tiny renderfarm. Hopefully this oversimplification will get you rendering a Bella scene on five computers by the end of the day. Once you are happy it works, I recommend you read Thinkbox's documentation to audit your security and performance and to explore all the advanced features.



## Overview
1. Introduce the various moving parts of the **renderfarm**
2. **Create** and **share** **`C:\\DeadlineRepository10`** on a Windows computer, this will be the  **`Repository`**
>    - pretend your server is named **`SAURON`**<sup>simplifies this guide</sup>
>    - **UNC path** would thus be **`\\SAURON\DeadlineRepository10`** 
3. **Create** a folder called **`C:\\DeadlineRepository10\BellaShared`**<sup>simplifies this guide</sup>
    - feel free to substitute your own network share
    - your Bella files, textures and references live here
4. Install **DeadlineRepository** software along with a MongoDB database on **`SAURON`** 
5. Run **DeadlineClient** and **BellaCLI** installers on five Windows computers ( including **`SAURON`** )
6. Copy **Bella** plugin scripts to **`\\\\SAURON\DeadlineRepository10\plugins\'**
7. Copy **Bella** submission scripts to **`\\\\SAURON\DeadlineRepository10\scripts\Submission\'**
8. Copy sample scenes to  **`\\\\SAURON\DeadlineRepository10\BellaShared\'**
9. From **`Computer_1`** right click **deadlinelauncher** in systemtray **Submit->BellaTimeOfDay**
10. Choose sample scene **\\\\SAURON\DeadlineRepository10\BellaShared\BellaTimeOfDay.bsx**  
11. Hit submit and go make a sandwich 
12. right click systemtray->**deadlinelauncher**->Launch **Monitor** to check on renderfarm


### Bella 

[**bella_cli-22.8.0.zip**](https://downloads.bellarender.com/bella_cli-22.8.0.zip?_ga=2.85371545.1442063462.1666750570-1596746247.1666283679)
>[Bella Render](https://bellarender.com) is a modern commercial path tracer developed by Diffuse Logic. DCC plugins, a standalone GUI and command line interface (CLI) are supported on MacOS and Windows. The CLI executable is available for Linux.
- A Bella license **include** 5 node licenses for command line rendering using: 
    - <sub>`C:\Program Files\Diffuse Logic\bella_cli.exe`</sub>
    ###### Renderfarm sidenotes:
    - Bella's **.bsz** file format wraps models and textures into a single file
    - **bella_cli.exe** has a **parseFragment** argument allowing sophisticated rendertime customizations
    - The Atlas solver can do cooperative rendering of a single scenefile on multiple computers
	- Deadline can add a post-render job to merge all renders into a single image
	- Saturn cooperative rendering support is planned

### Deadline 

>[Deadline](https://www.awsthinkbox.com/deadline) is renderfarm software developed by Thinkbox Software and owned by Amazon. Before August 2022 it was available with usage based licenses but is now [free of charge](https://aws.amazon.com/blogs/media/aws-thinkbox-products-now-available-free-of-charge/) on Windows, Mac and Linux.
> Download installers from https://awsthinkbox.com. An Amazon Web Services account is required. [Deadline's history](https://www.fxguide.com/quicktakes/aws-thinkbox-deadline-a-brief-history/)

#### Client Software 

`DeadlineClient-10.1.23.6-windows-installer.exe`

##### Here are some of the client programs in:
`C:\Program Files\Thinkbox\Deadline10\bin\`

##### Deadline's Launcher<sup>Hub for all tools</sup>
```
When you log into Windows, deadlinelauncher.exe runs
It is a useful hub to launch all other tools.
```

##### Deadline's Worker
```
deadlineworker.exe watches for jobs and then launches bella_cli
```

##### Deadline's Monitor
```
deadlinemonitor.exe displays all computers that can render
Along with monitoring, you can cancel, redirect, and submit jobs
```

---

#### Server Software 
`DeadlineRepository-10.1.23.6-windows.installer.exe`

The Deadline server provides instructions and render data to the clients

##### Repository
```
Shared renderfarm software and job data
Copy Bella plugin here and all clients can use it. 
```

##### Database
```
This accepts job submissions and tracks fullfillment.
```

## STEP A. Create a network share to host the `Deadline Repository`

remember we are playing pretend, where one of your computers is named Sauron
- Create folder **DeadlineRepository10** in C: drive on **SAURON** 
- right click **C:/DeadlineRepository10**->Properties->Sharing, click **Share**
- Add **Everyone**, change Permission Level to **Read/Write**. Click Share<sup>requires admin password</sub>

    - [x] **\\\\SAURON\DeadlineRepository10** <sup>network share</sup>
    - [x] all computers can read/write to **\\\\SAURON\\DeadlineRepository10**<sup>See official docs for security recommendations
    - [x] Sauron has **static** ip address not dhcp<sup>recommended for any server</sup>

## STEP B. Run Deadline Repository installer on Sauron

- DeadlineRepository-10.1.23.6-windows.installer.exe <sup>requires admin password</sup> 

**\\\\SAURON\DeadlineRepository10** should be interchangeable with  **C:\DeadlineRepository10** in this setup so either can be used. We already gave **Everyone** full read/write so either check or no check.

![](/assets/images/2022-10-26-14-50-07.png)

Choose **MongoDB** as the database, **new** installation, download, accept license

|![](/assets/images/2022-10-24-11-20-51.png) | ![](/assets/images/2022-10-24-11-21-35.png) |
|-------|-------:|
|![](/assets/images/2022-10-24-13-11-49.png)| ![](/assets/images/2022-10-24-13-12-19.png)|


- If you have more than one network device, make certain **MongoDB Hostname** is set to the correct IP address
- **MongoDB Port** is the network port that the **Workers** will connect on

![](/assets/images/2022-10-26-15-01-38.png)

For expediency we skip enhanced security<sup>see official recommendations</sup>, uncheck Require SSL

|![](/assets/images/2022-10-24-13-22-32.png)| ![](/assets/images/2022-10-24-13-23-48.png) |
|-------|-------:|
|![](/assets/images/2022-10-24-13-24-20.png)| 


## STEP C. Run installer on all computers<sup>including SAURON
***DeadlineClient-10.1.23.6-windows-installer.exe***

Even though Remote Connection Server is recommended, choose **Direct Connection** to remove a few steps

|![](/assets/images/2022-10-24-20-58-44.png)| ![](/assets/images/2022-10-24-20-59-04.png) |
|-------|-------:|
|![](/assets/images/2022-10-24-20-59-28.png)| ![](/assets/images/2022-10-24-21-00-46.png) |

- Click **Yes**, unless you lied about:
- [x] all computers can read and write to the **\\\\SAURON\\DeadlineRepository10**
- [ ] Check in File Explorer if unsure

![](/assets/images/2022-10-24-21-05-17.png)

|![](/assets/images/2022-10-24-21-05-52.png)|![](/assets/images/2022-10-24-21-11-32.png)|
|-------|-------:|
|![](/assets/images/2022-10-24-21-11-54.png)|![](/assets/images/2022-10-24-21-12-14.png)|

- Reboot and log into Windows
- **deadlinelauncher.exe** should start 
- if **not** start it C:\Program Files\Thinkbox\Deadline10\bin\deadlinelauncher.exe
- Windows Defender Firewall will ask for network permission<sup>admin password required</sup>
- **deadlineworker.exe** should also start  
- Windows Defender Firewall will ask for network permission<sup>admin password required</sup>
> When you start any Deadline app for the first time, Windows Defender Firewall will request permission

This popping up on your client computers means the **Deadline** Repository and Database were set up correctly

Click on the **Worker Information** tab

|![](/assets/images/2022-10-26-15-27-02.png)| ![](/assets/images/2022-10-26-15-31-24.png)|
|-------|-------:|

### Your renderfarm is ready to render

## STEP D: Install Bella CLI on all computers

- Make sure Bella CLI installs to this location
- `C:\Program Files\Diffuse Logic\Bella CLI\bella_cli.exe`

## STEP E: Install Deadline plugin for Bella from one computer
Get the code with
>git clone https://github.com/oomer/bellarenderfarm.git

or 

> https://github.com/oomer/bellarenderfarm/archive/refs/heads/main.zip


### Bella plugin directory with code and settings
- In the zip folder **bellarenderfarm**/DeadlineRepository10/custom/plugins/ copy the entire **Bella** directory to the **Repository**
 at \\\\SAURON\DeadlineRepository10\custom\plugins\

### Submission GUI code
- In the zip folder **bellarenderfarm**/DeadlineRepository10/custom/scripts/Submission/ copy the script **Bella.py** to the **Repository**
at \\SAURON\DeadlineRepository10\custom\scripts\Submission\

### Samples to get you started
- In the zip folder **bellarenderfarm**/DeadlineRepository10/ copy the entire **BellaShared** folder to the **Repository**
at \\SAURON\DeadlineRepository10\

Four files should look like this in the `Repository`
```sh
\\SAURON\DeadlineRepository10\custom\plugins\Bella\bella.ico
\\SAURON\DeadlineRepository10\custom\plugins\Bella\Bella.param
\\SAURON\DeadlineRepository10\custom\plugins\Bella\Bella.py
\\SAURON\DeadlineRepository10\custom\scripts\Submission\BellaSubmission.py
```

Optionally copy over the directory `BellaShared` to \\\\SAURON\DeadlineRepository10 if you need some bella samples

## STEP F: Submit a sample bella scene from the launcher
A GUI submission dailog is available from any machine you have installed **deadlinelauncher.exe** or **deadlinemonitor.exe**

In the systemtray, hovering over the Deadline Launcher icon should show your are connected
![](/assets/images/2022-10-31-12-44-19.png)

Right clicking on the systemtray deadline launcher will bring up the Submit menu
![](/assets/images/2022-10-31-12-49-30.png) 

File browse and directory browse making sure **Bella File** and **Image Output Directory** are both **network** accessible from all computers or else your render will fail. Hit Submit.
![](/assets/images/2022-10-31-12-51-37.png)

## STEP G: Submit a sample animation from the monitor
Right click on the systemtray deadline launcher and select **Launch Monitor**
the monitor should appear with 3 main areas Jobs, Task and Workers
![](/assets/images/2022-10-31-12-58-48.png)

>The Job area should have one entry for the bella submission you made in STEP F. If it is 100% completed blue or green and being worked on, that is good. 

Select the **Job** and the **Task** window will which computer worked on that task and the status. If you have errors, double click on the task and then double click on the log to show the rendering console output from bella_cli. 

> If you have errors, read the logs to figure out what the problem is.
90% of the time the problems are network related or permissions related. 

Try submitting the animation sequence 

![](/assets/images/2022-10-31-13-11-14.png)
Enjoy

