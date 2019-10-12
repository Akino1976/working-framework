library(methods)
#' USAGE: Object <- new("startUps", pkgs = .PACK, Input = c("data", "graf") )
#' CALL: Object$instant_pkgs( ), will update and install pkgs
#' CALL: Object$setDirs( Extra ), will create and set path
#'		to <Input> and if nessecary to the <Extra> character
startUps <- setRefClass("startUps",
			fields 	= list( pkgs = "character", Input = "character", path = "character" ),
			methods	= list(
				instant_pkgs = function( )
				{
					pkgs_miss <- pkgs[which(!pkgs %in% installed.packages()[, 1])]
    				if (length(pkgs_miss) > 0)
    				{
        				install.packages(pkgs_miss)
    				}

    				if (length( pkgs_miss) == 0)
    				{
        				message("\n ...Packages were already installed!\n")
    				}
   	     			attached <- search()
    				attached_pkgs <- attached[grepl("package", attached)]
    				need_to_attach <- pkgs[which(!pkgs %in% gsub("package:", "", attached_pkgs))]

    				if (length(need_to_attach) > 0)
    				{
        				for (i in 1:length(need_to_attach))
							require(need_to_attach[i], character.only = TRUE)
        }

					if (length(need_to_attach) == 0)
					{
        				message("\n ...Packages were already loaded!\n")
					}

				}, # End of function
				setDirs		= function( )
				{
					if( length(Input) > 0)
					{
						.HOME	<- path
						Input	<<- c(Input)
						if( inherits(Input, "character") )
						{
							Output	<- paste0(toupper(Input), " <- file.path('", .HOME, "','", Input, "')")

							for( d in Output)
							{
								cat("************************************************\n")
								String	<- gsub(".*\'(.*)\'.*", "\\1", toupper(d))
								cat("Path for", String , "completed\n")
								Step1 	<- parse(text = d)
								cat("************************************************\n")
								assign(String , eval(Step1), globalenv() )
								!file.exists(get( String )) && dir.create( get(String) ,
											 recursive = TRUE)
							} # ForLoop ends here
						} else {
							stop("Need to input character inside ", deparse(substitute(Input)))
						}
					}
					}	 ## End of function setDirs
			) # End of methodsList

) # End of setRefClass
