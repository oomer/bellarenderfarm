from __future__ import absolute_import
from System.IO import Path, File, Directory, StreamWriter
from System.Collections.Specialized import StringCollection
from System.Text import Encoding

from Deadline.Scripting import ClientUtils, RepositoryUtils, StringUtils, FrameUtils
from DeadlineUI.Controls.Scripting.DeadlineScriptDialog import DeadlineScriptDialog

from ThinkboxUI.Controls.Scripting.CheckBoxControl import CheckBoxControl
from ThinkboxUI.Controls.Scripting.RangeControl import RangeControl
from ThinkboxUI.Controls.Scripting.TextControl import TextControl
from ThinkboxUI.Controls.Scripting.ButtonControl import ButtonControl

scriptDialog = None
settings = None

def __main__():
    global scriptDialog
    global settings
    
    scriptDialog = DeadlineScriptDialog()
    scriptDialog.SetTitle( "Submit Bella Job To Deadline" )
    scriptDialog.SetIcon( RepositoryUtils.GetRepositoryFilePath("custom/plugins/Bella/bella.ico", True) )
    #scriptDialog.SetIcon( scriptDialog.GetIcon( 'Bella' ) )
    scriptDialog.SetSize( 512, 256)

    scriptDialog.AddTabControl( "Tabs", 0, 0 )

    # BELLA OPTIONS
    # =============
    scriptDialog.AddTabPage( "Bella Required Parameters" )
    scriptDialog.AddGrid()

    # Bella scene file chooser
    scriptDialog.AddControlToGrid( "sceneFileLabel", "LabelControl", "Bella File", 1, 0, "Choose Bella file to render", False )
    sceneFileObj = scriptDialog.AddSelectionControlToGrid( "sceneFileBox", "FileBrowserControl", "", "Bella Files (*.bs*);;All Files (*)", 1, 1, colSpan=5 )
    sceneFileObj.ValueModified.connect( autoDetectFrameRange )

    # Bella override directory 
    scriptDialog.AddControlToGrid( "outputDirectoryLabel", "LabelControl", "Image Output Directory", 2, 0, "Choose render save directory", False )
    scriptDialog.AddSelectionControlToGrid( "outputDirectoryBox", "FolderBrowserControl", "", "", 2, 1, colSpan=5 )
    
    scriptDialog.AddControlToGrid("sequenceFramesLabel", "LabelControl", "Frame Range", 3, 0, "Numeric frame range to render, ie 1-10", False)
    scriptDialog.AddControlToGrid("sequenceFramesBox", "TextControl", "", 3, 1, colSpan=1)
    scriptDialog.AddControlToGrid("sequenceFramesLabel2", "LabelControl", "Blank for single scenefile", 3, 2, "", False)

    scriptDialog.EndGrid()
    scriptDialog.EndTabPage() 
    
    # ANIMATION OPTIONS
    # =================
    scriptDialog.AddTabPage( "Animation" )
    scriptDialog.AddGrid()
    scriptDialog.EndGrid()
    scriptDialog.EndTabPage() 

    # DEADLINE OPTIONS
    # ================
    scriptDialog.AddTabPage( "Deadline Options" )
    scriptDialog.AddGrid()

    scriptDialog.AddControlToGrid( "nameLabel", "LabelControl", "Job Name", 1, 0, "The name of your job. This is optional, and if left blank, it will default to 'Untitled'.", False )
    scriptDialog.AddControlToGrid( "nameBox", "TextControl", "Untitled", 1, 1 )

    scriptDialog.AddControlToGrid( "commentLabel", "LabelControl", "Comment", 2, 0, "A simple description of your job. This is optional and can be left blank.", False )
    scriptDialog.AddControlToGrid( "commentBox", "TextControl", "", 2, 1 )

    scriptDialog.AddControlToGrid( "departmentLabel", "LabelControl", "Department", 3, 0, "The department you belong to. This is optional and can be left blank.", False )
    scriptDialog.AddControlToGrid( "departmentBox", "TextControl", "", 3, 1 )
    scriptDialog.EndGrid()

    scriptDialog.AddGrid()
    scriptDialog.AddControlToGrid( "separator22", "SeparatorControl", "Job Options", 0, 0, colSpan=3 )

    scriptDialog.AddControlToGrid( "poolLabel", "LabelControl", "Pool", 1, 0, "The pool that your job will be submitted to.", False )
    scriptDialog.AddControlToGrid( "poolBox", "PoolComboControl", "none", 1, 1 )

    scriptDialog.AddControlToGrid( "secondaryPoolLabel", "LabelControl", "Secondary Pool", 2, 0, "The secondary pool lets you specify a Pool to use if the primary Pool does not have any available Workers.", False )
    scriptDialog.AddControlToGrid( "secondaryPoolBox", "SecondaryPoolComboControl", "", 2, 1 )

    scriptDialog.AddControlToGrid( "groupLabel", "LabelControl", "Group", 3, 0, "The group that your job will be submitted to.", False )
    scriptDialog.AddControlToGrid( "groupBox", "GroupComboControl", "none", 3, 1 )

    scriptDialog.AddControlToGrid( "priorityLabel", "LabelControl", "Priority", 4, 0, "A job can have a numeric priority ranging from 0 to 100, where 0 is the lowest priority and 100 is the highest priority.", False )
    scriptDialog.AddRangeControlToGrid( "priorityBox", "RangeControl", RepositoryUtils.GetMaximumPriority() // 2, 0, RepositoryUtils.GetMaximumPriority(), 0, 1, 4, 1 )

    scriptDialog.AddControlToGrid( "taskTimeoutLabel", "LabelControl", "Task Timeout", 5, 0, "The number of minutes a Worker has to render a task for this job before it requeues it. Specify 0 for no limit.", False )
    scriptDialog.AddRangeControlToGrid( "taskTimeoutBox", "RangeControl", 0, 0, 1000000, 0, 1, 5, 1 )
    scriptDialog.AddSelectionControlToGrid( "isBlacklistBox", "CheckBoxControl", False, "Machine List Is A Deny List", 5, 2, "Use the Machine Limit to specify the maximum number of machines that can render your job at one time. Specify 0 for no limit." )

    scriptDialog.AddControlToGrid( "machineListLabel", "LabelControl", "Machine List", 6, 0, "The list of machines on the deny list or allow list.", False )
    scriptDialog.AddControlToGrid( "machineListBox", "MachineListControl", "", 6, 1, colSpan=2 )

    scriptDialog.AddControlToGrid( "limitGroupLabel", "LabelControl", "Limits", 7, 0, "The Limits that your job requires.", False )
    scriptDialog.AddControlToGrid( "limitGroupBox", "LimitGroupControl", "", 7, 1, colSpan=2 )

    scriptDialog.AddControlToGrid( "dependencyLabel", "LabelControl", "Dependencies", 8, 0, "Specify existing jobs that this job will be dependent on. This job will not start until the specified dependencies finish rendering. ", False )
    scriptDialog.AddControlToGrid( "dependencyBox", "DependencyControl", "", 8, 1, colSpan=2 )

    scriptDialog.AddControlToGrid( "onJobCompleteLabel", "LabelControl", "On Job Complete", 9, 0, "If desired, you can automatically archive or delete the job when it completes. ", False )
    scriptDialog.AddControlToGrid( "onJobCompleteBox", "OnJobCompleteControl", "Nothing", 9, 1 )
    scriptDialog.AddSelectionControlToGrid( "submitSuspendedBool", "CheckBoxControl", False, "Submit Job As Suspended", 9, 2, "If enabled, the job will submit in the suspended state. This is useful if you don't want the job to start rendering right away. Just resume it from the Monitor when you want it to render. " )
    scriptDialog.EndGrid()
    scriptDialog.EndTabPage() 

    scriptDialog.EndTabControl() 

    # Global 
    scriptDialog.AddGrid()
    scriptDialog.AddControlToGrid( "Separator3", "SeparatorControl", "Bella Overrides", 2, 0, colSpan=10 )
    scriptDialog.AddControlToGrid( "outputExtLabel", "LabelControl", "Image Format", 8, 0, "Image format" )
    outputExtList = ("default", ".png",".jpg",".exr",".tga",".bmp","tif",".iff",".dpx",".hdr")
    scriptDialog.AddComboControlToGrid( "outputExtCombo", "ComboControl", "default", outputExtList, 8, 1, "Image format, default uses setting set in .bsx" )
    resolutionOverrideObj = scriptDialog.AddSelectionControlToGrid( "resolutionOverrideBool", "CheckBoxControl", False, "Resolution", 8, 3, "Enable resolution override" )
    resolutionOverrideObj.ValueModified.connect( enableResolutionOverride )
    scriptDialog.AddControlToGrid( "widthLabel", "LabelControl", "Width", 8, 4, "Image Width" )
    scriptDialog.AddRangeControlToGrid( "widthBox", "RangeControl", 800, 1, 10000, 0, 1, 8, 5, "Width" )
    scriptDialog.SetEnabled( "widthLabel", False )
    scriptDialog.SetEnabled( "widthBox", False )
    scriptDialog.AddControlToGrid( "heightLabel", "LabelControl", "Height", 8, 6, "Image Height" )
    scriptDialog.AddRangeControlToGrid( "heightBox", "RangeControl", 600, 1, 50000, 0, 1, 8, 7, "Height" )
    scriptDialog.SetEnabled( "heightLabel", False )
    scriptDialog.SetEnabled( "heightBox", False )
    targetNoiseOverrideObj = scriptDialog.AddSelectionControlToGrid( "targetNoiseOverrideBool", "CheckBoxControl", False, "Target Noise", 10, 0, "Enable targetNoise override" )
    targetNoiseOverrideObj.ValueModified.connect( enableTargetNoiseOverride )
    scriptDialog.AddRangeControlToGrid( "targetNoiseBox", "RangeControl", 6, 1, 20, 0, 1, 10, 2, "Target Noise, higher less noise" )
    scriptDialog.SetEnabled( "targetNoiseBox", False )
    scriptDialog.AddSelectionControlToGrid( "denoiseOverrideBool", "CheckBoxControl", False, "Denoise", 11, 0, "Enable denoising" )
    scriptDialog.AddControlToGrid("denoiseBox", "TextControl", "", 11, 1, colSpan=3)
    scriptDialog.AddSelectionControlToGrid( "timeLimitOverrideBool", "CheckBoxControl", False, "Time Limit", 12, 0, "Stop render before target noise is reached" )
    scriptDialog.AddRangeControlToGrid( "timeLimitBox", "RangeControl", 1, 0, 50000, 0, 1, 12, 2, "Time Limit in minutes" )


    scriptDialog.AddHorizontalSpacerToGrid( "HSpacer1", 0, 0 )
    submitButton = scriptDialog.AddControlToGrid( "submitButton", "ButtonControl", "Submit", 0, 7, expand=False )
    submitButton.ValueModified.connect(submitButtonPressed)
    closeButton = scriptDialog.AddControlToGrid( "closeButton", "ButtonControl", "Close", 0, 8, expand=False )
    closeButton.ValueModified.connect(scriptDialog.closeEvent)
    scriptDialog.AddHorizontalSpacerToGrid( "HSpacer1", 1, 0 )
    scriptDialog.EndGrid()
    
    # Convenience auto save of previous submission
    settings = ("departmentBox","poolBox","secondaryPoolBox","groupBox","priorityBox","isBlacklistBox","machineListBox","limitGroupBox",
                "sceneFileBox",
                "outputDirectoryBox",
                "sequenceFramesBox",
                "outputExtCombo",
                "resolutionOverrideBool",
                "widthBox",
                "heightBox",
                "targetNoiseOverrideBool",
                "targetNoiseBox",
                "denoiseOverrideBool",
                "timeLimitOverrideBool",
                "timeLimitBox",
                )
    settingsFile =  Path.Combine( ClientUtils.GetUsersSettingsDirectory(), "BellaSettings.ini" )
    scriptDialog.LoadSettings( settingsFile, settings )
    scriptDialog.EnabledStickySaving( settings, settingsFile )
    scriptDialog.ShowDialog( False )
    
def enableResolutionOverride( *args ):
    global scriptDialog
    resolutionOverrideBool = scriptDialog.GetValue( "resolutionOverrideBool" )
    scriptDialog.SetEnabled( "widthLabel", resolutionOverrideBool )
    scriptDialog.SetEnabled( "widthBox", resolutionOverrideBool )
    scriptDialog.SetEnabled( "heightLabel", resolutionOverrideBool )
    scriptDialog.SetEnabled( "heightBox", resolutionOverrideBool )

def enableTargetNoiseOverride( *args ):
    global scriptDialog
    targetNoiseOverrideBool = scriptDialog.GetValue( "targetNoiseOverrideBool" )
    scriptDialog.SetEnabled( "targetNoiseBox", targetNoiseOverrideBool )

def enableSequenceOverride( *args ):
    global scriptDialog
    sequenceOverrideBool = scriptDialog.GetValue( "sequenceOverrideBool" )
    scriptDialog.SetEnabled( "sequenceFramesLabel", sequenceOverrideBool )
    scriptDialog.SetEnabled( "sequenceFramesBox", sequenceOverrideBool )

def autoDetectFrameRange( *args ):
    global scriptDialog
    sceneFile = scriptDialog.GetValue( "sceneFileBox" )
    sequenceFramesString = ''
    try:
        selectedFrame = FrameUtils.GetFrameNumberFromFilename( sceneFile )
        paddingSize = FrameUtils.GetPaddingSizeFromFilename( sceneFile )
        startFrame = FrameUtils.GetLowerFrameRange(sceneFile, selectedFrame, paddingSize )
        endFrame = FrameUtils.GetUpperFrameRange( sceneFile, selectedFrame, paddingSize )
        if startFrame == endFrame: sequenceFramesString = str(startFrame)
        else: sequenceFramesString = str(startFrame) + "-" + str(endFrame)
    except:
        sequenceFramesString = ""
    scriptDialog.SetValue( "sequenceFramesBox", sequenceFramesString )


def submitButtonPressed(*args):
    global scriptDialog
    outputDirectory = scriptDialog.GetValue( "outputDirectoryBox" )

    if( not Directory.Exists( outputDirectory ) ):
        scriptDialog.ShowMessageBox( "Output Directory %s does not exist" % outputDirectory, "Error" )
        return

    if not scriptDialog.GetValue( "sequenceFramesBox") == "":
        print('seuquence')

        # Checks
        sceneFile = scriptDialog.GetValue( "sceneFileBox" )

        sequenceFramesString =  scriptDialog.GetValue( "sequenceFramesBox" ) 
        if not FrameUtils.FrameRangeValid( sequenceFramesString ):
            scriptDialog.ShowMessageBox( "Frame range string is invalid, should be in form 1-10", "Error" )
            return

        sequenceFramesPadding = FrameUtils.GetPaddingSizeFromFilename( sceneFile)
        print(sequenceFramesPadding)
        print(FrameUtils.GetLowerFrameFilename( sceneFile, 0, sequenceFramesPadding  ))
        startFrame = FrameUtils.GetLowerFrameRange( sceneFile, 0, sequenceFramesPadding  )
        endFrame = FrameUtils.GetUpperFrameRange( sceneFile, 1, sequenceFramesPadding  )
        startFramePadded = str(startFrame).zfill(sequenceFramesPadding)
        endFramePadded = str(endFrame).zfill(sequenceFramesPadding)

        print(FrameUtils.SubstituteFrameNumber( sceneFile, startFramePadded) )
        print(FrameUtils.SubstituteFrameNumber( sceneFile, endFramePadded ))

        if len( sceneFile ) == 0:
            scriptDialog.ShowMessageBox( "No Bella sequence file specified", "Error" )
            return
        if not File.Exists( sceneFile ):
            scriptDialog.ShowMessageBox( "Bella file %s does not exist" % sceneFile, "Error" )
            return

        # Create job info file.
        jobName = scriptDialog.GetValue( "nameBox" )
        jobInfoFilename = Path.Combine( ClientUtils.GetDeadlineTempPath(), "bella00_job_info.job" )
        writer = StreamWriter( jobInfoFilename, False, Encoding.Unicode )
        writer.WriteLine( "Plugin=Bella" )
        writer.WriteLine( "Name=%s" % jobName )
        writer.WriteLine( "Comment=%s" % scriptDialog.GetValue( "commentBox" ) )
        writer.WriteLine( "Department=%s" % scriptDialog.GetValue( "departmentBox" ) )
        writer.WriteLine( "Pool=%s" % scriptDialog.GetValue( "poolBox" ) )
        writer.WriteLine( "SecondaryPool=%s" % scriptDialog.GetValue( "secondaryPoolBox" ) )
        writer.WriteLine( "Group=%s" % scriptDialog.GetValue( "groupBox" ) )
        writer.WriteLine( "Priority=%s" % scriptDialog.GetValue( "priorityBox" ) )
        writer.WriteLine( "TaskTimeoutMinutes=%s" % scriptDialog.GetValue( "taskTimeoutBox" ) )
        
        if( bool(scriptDialog.GetValue( "isBlacklistBox" )) ):
            writer.WriteLine( "Blacklist=%s" % scriptDialog.GetValue( "machineListBox" ) )
        else:
            writer.WriteLine( "Whitelist=%s" % scriptDialog.GetValue( "machineListBox" ) )
        
        writer.WriteLine( "LimitGroups=%s" % scriptDialog.GetValue( "limitGroupBox" ) )
        writer.WriteLine( "JobDependencies=%s" % scriptDialog.GetValue( "dependencyBox" ) )
        writer.WriteLine( "OnJobComplete=%s" % scriptDialog.GetValue( "onJobCompleteBox" ) )
        
        if( bool(scriptDialog.GetValue( "submitSuspendedBool" )) ):
            writer.WriteLine( "InitialStatus=Suspended" )
        
        writer.WriteLine( "MachineLimit=5" )
        writer.WriteLine( "Frames=%s" % scriptDialog.GetValue( "sequenceFramesBox" )  ) 
        writer.WriteLine( "ChunkSize=1" )
        writer.Close()

        # Create plugin info file.
        pluginInfoFilename = Path.Combine( ClientUtils.GetDeadlineTempPath(), "bella_plugin_info.job" )
        writer = StreamWriter( pluginInfoFilename, False, Encoding.Unicode )

        # Required
        writer.WriteLine("sceneFile=" + sceneFile)
        writer.WriteLine( "outputDirectory=%s" % outputDirectory )
        # Optionals
        if scriptDialog.GetValue( "resolutionOverrideBool") :
            writer.WriteLine( "imageWidth=%s" % scriptDialog.GetValue( "widthBox" ) )
            writer.WriteLine( "imageHeight=%s" % scriptDialog.GetValue( "heightBox" ) )
        if scriptDialog.GetValue( "targetNoiseOverrideBool" ):
            writer.WriteLine( "targetNoise=%s" % scriptDialog.GetValue( "targetNoiseBox" ) )
        if scriptDialog.GetValue( "denoiseOverrideBool" ):
            writer.WriteLine( "denoise=%s" % scriptDialog.GetValue( "denoiseBox" ) )
        if scriptDialog.GetValue( "timeLimitOverrideBool" ):
            writer.WriteLine( "timeLimit=%s" % scriptDialog.GetValue( "timeLimitBox" ) )
        writer.WriteLine( "replaceFrameNumber=false" )
        writer.Close()
        # Setup the command line arguments.
        arguments = StringCollection()
        
        arguments.Add( jobInfoFilename )
        arguments.Add( pluginInfoFilename )
        report = ClientUtils.ExecuteCommandAndGetOutput( arguments )
        scriptDialog.ShowMessageBox( report, "Sequence submission report" )
        scriptDialog.CloseDialog()

    else:
        sceneFile = scriptDialog.GetValue( "sceneFileBox" )

        if len( sceneFile ) == 0:
            scriptDialog.ShowMessageBox( "No Bella file specified", "Error" )
            return

        if not File.Exists( sceneFile ):
            scriptDialog.ShowMessageBox( "Bella file %s does not exist" % sceneFile, "Error" )
            return

        jobName = scriptDialog.GetValue( "nameBox" )

        # Create job info file.
        jobInfoFilename = Path.Combine( ClientUtils.GetDeadlineTempPath(), "bella_job_info.job" )
        writer = StreamWriter( jobInfoFilename, False, Encoding.Unicode )
        writer.WriteLine( "Plugin=Bella" )
        writer.WriteLine( "Name=%s" % jobName )
        writer.WriteLine( "Comment=%s" % scriptDialog.GetValue( "commentBox" ) )
        writer.WriteLine( "Department=%s" % scriptDialog.GetValue( "departmentBox" ) )
        writer.WriteLine( "Pool=%s" % scriptDialog.GetValue( "poolBox" ) )
        writer.WriteLine( "SecondaryPool=%s" % scriptDialog.GetValue( "secondaryPoolBox" ) )
        writer.WriteLine( "Group=%s" % scriptDialog.GetValue( "groupBox" ) )
        writer.WriteLine( "Priority=%s" % scriptDialog.GetValue( "priorityBox" ) )
        writer.WriteLine( "TaskTimeoutMinutes=%s" % scriptDialog.GetValue( "taskTimeoutBox" ) )
        
        if( bool(scriptDialog.GetValue( "isBlacklistBox" )) ):
            writer.WriteLine( "Blacklist=%s" % scriptDialog.GetValue( "machineListBox" ) )
        else:
            writer.WriteLine( "Whitelist=%s" % scriptDialog.GetValue( "machineListBox" ) )
        
        writer.WriteLine( "LimitGroups=%s" % scriptDialog.GetValue( "limitGroupBox" ) )
        writer.WriteLine( "JobDependencies=%s" % scriptDialog.GetValue( "dependencyBox" ) )
        writer.WriteLine( "OnJobComplete=%s" % scriptDialog.GetValue( "onJobCompleteBox" ) )
        
        if( bool(scriptDialog.GetValue( "submitSuspendedBool" )) ):
            writer.WriteLine( "InitialStatus=Suspended" )
        
        writer.WriteLine( "MachineLimit=1" )
        writer.WriteLine( "Frames=0" )
        writer.WriteLine( "ChunkSize=1" )
        
        writer.Close()

        # Create plugin info file.
        pluginInfoFilename = Path.Combine( ClientUtils.GetDeadlineTempPath(), "bella_plugin_info.job" )
        writer = StreamWriter( pluginInfoFilename, False, Encoding.Unicode )

        # Required Parameters
        writer.WriteLine("sceneFile=" + sceneFile)
        writer.WriteLine( "outputDirectory=%s" % scriptDialog.GetValue( "outputDirectoryBox" ) )
        
        # Overrides
        if scriptDialog.GetValue( "resolutionOverrideBool") :
            writer.WriteLine( "imageWidth=%s" % scriptDialog.GetValue( "widthBox" ) )
            writer.WriteLine( "imageHeight=%s" % scriptDialog.GetValue( "heightBox" ) )
        if scriptDialog.GetValue( "targetNoiseOverrideBool" ):
            writer.WriteLine( "targetNoise=%s" % scriptDialog.GetValue( "targetNoiseBox" ) )
        if scriptDialog.GetValue( "denoiseOverrideBool" ):
            writer.WriteLine( "denoise=%s" % scriptDialog.GetValue( "denoiseBox" ) )
        if scriptDialog.GetValue( "timeLimitOverrideBool" ):
            writer.WriteLine( "timeLimit=%s" % scriptDialog.GetValue( "timeLimitBox" ) )
        writer.WriteLine( "outputExt=%s" % scriptDialog.GetValue( "outputExtCombo" ) )
        #writer.WriteLine( "replaceFrameNumber=false" )
        writer.Close()

        # Submit job
        arguments = StringCollection()
        arguments.Add( jobInfoFilename )
        arguments.Add( pluginInfoFilename )
        report = ClientUtils.ExecuteCommandAndGetOutput( arguments )
        scriptDialog.ShowMessageBox( report, "Scene submission report" )
        scriptDialog.CloseDialog()
