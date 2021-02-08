library(data.table)
library(stringr)
library(plyr)
library(stats)
library(reshape)

setwd("~/Desktop/NBA_Model")

#pull and clean data from a given year
pull_year<-function(year){
  sub_sheet<-data.frame()
  
  #pull all the box scores
  file_list<-list.files(path=paste0("~/Desktop/NBA_Model/box_scores_new/",year))
  for(i in 1:length(file_list)){
    box<-data.frame(fread(paste0("box_scores_new/",year,"/",file_list[i])))
    box$id <- gsub("\\.csv","",file_list[i])
    sub_sheet<-rbind.fill(sub_sheet,box)
  }
  names(sub_sheet)[1]<-"name"
  
  #convert to numeric
  for(col_num in 4:(ncol(sub_sheet)-1)){
    sub_sheet[,col_num]<-as.numeric(sub_sheet[,col_num])
  }
  sub_sheet<-sub_sheet[sub_sheet$min>0,]
  
  #get the minutes in numeric form
  sub_sheet$min_num<-
    as.numeric(substr(sub_sheet$min,1,2))+
    (1/60)*(as.numeric(substr(sub_sheet$min,4,5)))
  sub_sheet[is.na(sub_sheet$min_num),]$min_num<-
    as.numeric(substr(sub_sheet[is.na(sub_sheet$min_num),]$min,1,1))+
    (1/60)*(as.numeric(substr(sub_sheet[is.na(sub_sheet$min_num),]$min,3,4)))
  
  #get two-pointers
  sub_sheet$X2pa <- sub_sheet$fga-sub_sheet$X3pa
  sub_sheet$X2pm <- sub_sheet$fgm-sub_sheet$X3pm
  
  
  #get OT flag
  min_df<-aggregate(sub_sheet$min_num,by=list(sub_sheet$id,sub_sheet$team),FUN=sum)
  names(min_df)<-c("id","team","min")
  min_df$min<-round(min_df$min,0)/5
  min_df$ot<-(min_df$min-48)/5
  sub_sheet$ot<-min_df$ot[match(sub_sheet$id,min_df$id)]
  
  #get net margin
  sub_sheet$net_margin<-
    sub_sheet$plusminus/sub_sheet$min_num-
    (sub_sheet$margin-sub_sheet$plusminus)/
    (48+sub_sheet$ot*5-sub_sheet$min_num)

  #list variables to actually keep
  keep<-c("name","team","min","fgm","fga","X3pm","X3pa","ftm","fta","orb","drb",
          "ast","stl","blk","tov","pf","pts","defrtg","pace","spd","dist","orbc",
          "drbc","tchs","sast","ftast","pass","cfgm","cfga","dfgm","dfga",
          "min_num","net_margin","ot","id","X2pa","X2pm","offrtg")
  sub_sheet<-sub_sheet[,(names(sub_sheet) %in% keep)]
  
  #get number of possessions
  sub_sheet$num_poss<-(sub_sheet$pace/48)*sub_sheet$min_num
  
  #eliminate people with nearly no minutes
  sub_sheet<-sub_sheet[sub_sheet$min_num>5,]
  
  return(sub_sheet)
}

#combine all the year data
get_full_box_hist<-function(){
  
  #initialize the dataframe
  full_sheet_pre<-data.frame()
  
  for(year in 2014:2020){
    #time for accountability purposes (see if running slow)
    start_time<-Sys.time()
    
    #get the data from each year
    sub_sheet<-pull_year(year)
    
    #combine the data
    full_sheet_pre<-rbind(full_sheet_pre,sub_sheet)
    print(paste(year, "is done in", Sys.time()-start_time))
  }
  #write the full stats (small file since all are saved as integers)
  fwrite(full_sheet_pre,"full_nba_stats_hist.csv")
  
  #return the file
  return(full_sheet_pre)
}

#scale and normalize the full data 
scale_by_poss<-function(df){
  #eliminate games with missing net_margin info (<0.1% of games)
  df<-df[is.na(df$net_margin)==FALSE,]
  
  #eliminate games with missing table info (<0.5% of games)
  df<-df[is.na(df$dfga)==FALSE&is.na(df$pace)==FALSE&is.na(df$ast)==FALSE,]
  
  #eliminates games where the website box score data is wrong 
  df<-df[df$ot>=0,] 
  
  #eliminates games (~<0.1%) where players play every minute (no on-off data)
  df<-df[df$net_margin<10|df$net_margin>-10,]

  #store mean and standard deviation to convert back
  info<-data.frame(sd(df$offrtg),sd(df$defrtg),sd(df$net_margin),
                   mean(df$offrtg),mean(df$defrtg),mean(df$net_margin))
  fwrite(info,"data/info_conversions.csv")
  
  #make all data per-possession except for those excluded
  exclude<-c("name","team","min","min_num","num_poss","net_margin","offrtg",
            "defrtg","spd","pace","id","ot")
  df[,!(names(df) %in% exclude)]<-df[,!(names(df) %in% exclude)]/df$num_poss
  
  #normalize all data except for those excluded
  no_scale<-c("name","team","min","net_margin","id","ot","num_poss")
  df[,!(names(df) %in% no_scale)]<-scale(df[,!(names(df) %in% no_scale)])

  #write the file
  fwrite(df,"data/full_nba_stats_hist_scaled.csv")
  return(df)
}

#call all the functions in order
pull_history<-function(){
  full_sheet_pre<-get_full_box_hist()
  full_sheet_pre<-scale_by_poss(full_sheet_pre)
  return(full_sheet_pre)
}

df<-pull_history()

