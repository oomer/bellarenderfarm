#!/usr/bin/env python3
import shutil
from Deadline.Plugins import *
from Deadline.Scripting import FileUtils, SystemUtils, RepositoryUtils, FileUtils, PathUtils, FrameUtils, StringUtils
from System.Diagnostics import *
from pathlib import Path
import shutil

def GetDeadlinePlugin():
    """Deadline calls to get an instance of DeadlinePlugin class"""
    return BellaPlugin()

def CleanupDeadlinePlugin(deadlinePlugin):
    """Deadline calls this when the plugin is no longer in use"""
    deadlinePlugin.Cleanup()

class BellaPlugin(DeadlinePlugin):
    sceneFile = ""
    def __init__(self):
        """setup Deadline callbacks"""
        self.InitializeProcessCallback += self.InitializeProcess
        self.PreRenderTasksCallback += self.PreRenderTasks
        self.RenderExecutableCallback += self.RenderExecutable
        self.RenderArgumentCallback += self.RenderArgument

    def Cleanup(self):
        """Clean up the plugin."""
        # Clean up stdout handler callbacks
        for stdoutHandler in self.StdoutHandlers:
            del stdoutHandler.HandleCallback

        del self.InitializeProcessCallback
        del self.RenderExecutableCallback
        del self.RenderArgumentCallback

    def InitializeProcess(self):
        """Called by Deadline"""
        self.SingleFramesOnly = False
        self.PluginType = PluginType.Simple

        self.ProcessPriority = ProcessPriorityClass.BelowNormal
        self.UseProcessTree = True
        self.StdoutHandling = True

        self.AddStdoutHandlerCallback(
            "(\[WARNING\])").HandleCallback += self.HandleStdoutWarning
        # [ ] bella_cli currently has a lot of non critical error messages
        # [ ] should be critical for texture or reference fails
        # [ ] should allow the user to have a strict mode, I think bella_cli support is planned for strict
        #self.AddStdoutHandlerCallback(
        #    "(\[ERROR\])").HandleCallback += self.HandleStdoutError
        self.AddStdoutHandlerCallback( 
            "(Progress: [0-9]*.[0-9]*%)" ).HandleCallback += self.HandleProgress

    def HandleStdoutWarning(self):
        self.LogWarning(self.GetRegexMatch(0))

    def HandleStdoutError(self):
        self.FailRender("Error: " + self.GetRegexMatch(1))

    def HandleProgress( self ):
        # Regex input is in string form "Progress: 68.78%""
        self.SetProgress( float(self.GetRegexMatch(1)[9:-1]) )

    def PreRenderTasks( self ):
        # This Plugin instance knows what frame it is working on via self.getStartFrame()
        # Substitute work frame into sceneFile string
        self.sceneFile = self.GetPluginInfoEntry( "sceneFile" ).strip()
        self.sceneFile = RepositoryUtils.CheckPathMapping( self.sceneFile )
        
        sceneFileFramePadded = FrameUtils.GetFrameStringFromFilename( self.sceneFile )
        paddingSize = len( sceneFileFramePadded )
        #print('userFramePadded', sceneFileFramePadded, 'paddingSize', paddingSize) 
        if paddingSize > 0:
            renderFramePadded = StringUtils.ToZeroPaddedString( self.GetStartFrame(), paddingSize, False )
            #print('renderFramePadded',renderFramePadded)
            self.sceneFile = FrameUtils.SubstituteFrameNumber( self.sceneFile, renderFramePadded )

    def RenderExecutable(self):
        """Callback to get executable used for rendering"""
        executableList =  self.GetConfigEntry("BellaPluginRenderExecutable")
        # Goes through semi colon separated list of paths in Bella.param
        # Uses default Diffuse Logic install location for Windows, MacOS and Linux Bella CLI
        executable = FileUtils.SearchFileList( executableList )
        if( executable == "" ): self.FailRender( "Bella render executable not found in plugin search paths" )
        return executable

    def RenderArgument(self):
        """Callback to get arguments passed to the executable"""
        sceneFile = self.sceneFile
        sceneFile = RepositoryUtils.CheckPathMapping( sceneFile )   # remap path for worker's OS
        outputDirectory = self.GetPluginInfoEntry( "outputDirectory" ).strip()  
        outputDirectory = RepositoryUtils.CheckPathMapping( outputDirectory )   
        outputExt = self.GetPluginInfoEntryWithDefault( "outputExt", "").strip()
        imageWidth = self.GetPluginInfoEntryWithDefault( "imageWidth", "").strip()
        imageHeight = self.GetPluginInfoEntryWithDefault( "imageHeight", "").strip()
        targetNoise = self.GetPluginInfoEntryWithDefault( "targetNoise", "").strip()
        useGpu = self.GetPluginInfoEntryWithDefault( "useGpu", "").strip()
        timeLimit = self.GetPluginInfoEntryWithDefault( "timeLimit", "").strip()
        denoiseName = self.GetPluginInfoEntryWithDefault( "denoise", "").strip()

        # [ ] do this in PreRenderTasks, needs cross platform testing 
        if SystemUtils.IsRunningOnWindows():
            sceneFile = sceneFile.replace( "/", "\\" )
            outputDirectory = outputDirectory.replace( "/", "\\" )
            if sceneFile.startswith( "\\" ) and not sceneFile.startswith( "\\\\" ):
                sceneFile = "\\" + sceneFile
            if outputDirectory.startswith( "\\" ) and not outputDirectory.startswith( "\\\\" ):
                outputDirectory = "\\" + outputDirectory
        else:
            sceneFile = sceneFile.replace( "\\", "/" )

        sceneFilePathlib = Path(sceneFile)
        sceneFileStem = sceneFilePathlib.stem
        sceneFileSuffix = sceneFilePathlib.suffix
        # [ ] Had issue with .bsz res directory failing creation by bella_cli
        # created /tmp/res manually and it worked
        tempPath = Path(PathUtils.GetSystemTempPath())
        print(tempPath,sceneFileSuffix)

        '''disabling .bsz copy
        if sceneFileSuffix == ".bsz":
            # Make a local copy of the sceneFile when rendering a .bsz to prevent unzip clashes with multiple machines
            # [ ] maybe always make a local copy to limit network traffic
            # [ ] need to figure out how to clean up temp directory postjob
            tempSceneFile = str(tempPath / sceneFilePathlib.name)
            shutil.copy(sceneFile, tempSceneFile)
            arguments = " -i:%s" % tempSceneFile
        else:
            arguments = " -i:%s" % sceneFile
        '''
        arguments = " -i:\"%s\"" % sceneFile
        arguments += " -pf:\"beautyPass.overridePath=null;\""

        if outputExt == ".png" or outputExt == "default":
            outputExt = "" # [ ] HACK, parseFragment has no method to unset .outputExt properly ( like null )  
        arguments += " -pf:\"beautyPass.outputExt=\\\"%s\\\";\"" % outputExt
        arguments += " -pf:\"beautyPass.outputName=\\\"%s\\\";\"" % sceneFileStem
        # [ ] Warning: sceneFile name used for the outputName, to avoid name clashing by blindly using what is set in bella
        # bella_cli will fail when the outputName has the string default anywhere

        if not targetNoise == "":
            arguments += " -pf:\"beautyPass.targetNoise=%su;\"" % targetNoise
        if not useGpu == "":
            arguments += " -pf:\"settings.useGpu=true;\"" 
        if not timeLimit == "":
            arguments += " -pf:\"beautyPass.timeLimit=%sf;\""  % timeLimit
        if not denoiseName == "":
            arguments += " -pf:\"beautyPass.denoise=true; beautyPass.denoiseOutputName=\\\"%s\\\";\"" % denoiseName

        arguments += " -od:\"%s\"" % outputDirectory
        arguments += " -vo" 
        if not imageWidth == "":
            arguments += " -res:\"%sx%s\"" %(imageWidth,imageHeight)
        return arguments