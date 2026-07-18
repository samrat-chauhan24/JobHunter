on run {input, parameters}
	
	set dialogText to ¬
		"Welcome to JobHunter" & return & return & ¬
		"Select an operation:" & return & return & ¬
		"Launch JobHunter" & return & ¬
		"Starts Docker Desktop, the JobHunter container and the Search API." & return & return & ¬
		"Run Auto Applier" & return & ¬
		"Launches the Auto Applier in Terminal." & return & return & ¬
		"Stop JobHunter" & return & ¬
		"Stops all JobHunter services."
	
	try
		set choice to button returned of (display dialog dialogText ¬
			with title "JobHunter" ¬
			buttons {"Stop JobHunter", "Run Auto Applier", "Launch JobHunter"} ¬
			default button "Launch JobHunter" ¬
			with icon note)
	on error number -128
		return input
	end try
	
	
	----------------------------------------------------------
	-- Launch JobHunter
	----------------------------------------------------------
	if choice is "Launch JobHunter" then
		
		try
			
			do shell script "/Users/rajputana.sam/Documents/JobHunter/macOS_Launcher/launch.sh"
			
			display notification "JobHunter startup initiated." with title "JobHunter"
			
		on error errMsg number errNum
			
			display dialog "Launch Failed" & return & return & ¬
				"Error " & errNum & return & return & errMsg ¬
				buttons {"OK"} default button 1 with icon stop
			
		end try
		
		
	----------------------------------------------------------
	-- Run Auto Applier
	----------------------------------------------------------
	else if choice is "Run Auto Applier" then
		
		try
			
			tell application "Terminal"
				activate
				do script "/Users/rajputana.sam/Documents/JobHunter/macOS_Launcher/run_applier.sh"
			end tell
			
			display notification "Auto Applier started." with title "JobHunter"
			
		on error errMsg number errNum
			
			display dialog "Unable to Launch Auto Applier" & return & return & ¬
				"Error " & errNum & return & return & errMsg ¬
				buttons {"OK"} default button 1 with icon stop
			
		end try
		
		
	----------------------------------------------------------
	-- Stop JobHunter
	----------------------------------------------------------
	else if choice is "Stop JobHunter" then
		
		try
			
			do shell script "/Users/rajputana.sam/Documents/JobHunter/macOS_Launcher/stop.sh"
			
			display notification "JobHunter stopped." with title "JobHunter"
			
		on error errMsg number errNum
			
			display dialog "Stop Failed" & return & return & ¬
				"Error " & errNum & return & return & errMsg ¬
				buttons {"OK"} default button 1 with icon stop
			
		end try
		
	end if
	
	return input
	
end run