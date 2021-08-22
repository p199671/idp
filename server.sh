#!/bin/bash                                                                     
                                                                                
echo "Getting $(pos_get_variable hostname) up to date."                         
apt -y update                                                                   
apt -y upgrade                                                                  
                                                                                
echo "Update & upgrade done." 
