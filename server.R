library(ggplot2)
library(tidyverse)
library(lubridate)
function(input, output, session) {
  
  all_data = NULL
  
  greeks = list("p_vega", "p_delta", "p_theta", "p_gamma", "c_vega", "c_delta", "c_theta", "c_gamma")
  calc_greeks <- function(input){
    total_data = list()
    path_root = paste0(input, "/greeks")
    path_dates = paste0(path_root, "/Dates")[[1]]
    dates = substring(gsub("\t","",unlist(read.csv(path_dates))), 2)
    for (i in 1:length(dates)){
      data = list()
      path = paste0(path_root, "/", dates[i], "/")
      temp = list.files(path = path, pattern="*.csv")
      myfiles = lapply(paste0(path,temp), read.delim)
      for (j in 1:length(greeks)){
        z = data.frame()
        for (k in 1:length(myfiles)){
          df = eval(parse(text=paste("myfiles[[k]]$", toString(greeks[j]), sep = "")))
          #print (df)
          z = rbind(z,df)
        }
        rownames(z) = c(as.POSIXlt(gsub(".csv", "", gsub("A", "", gsub("%", ":", temp)))))
        z = data.matrix(z)
        colnames(z) = myfiles[[1]]$X
        data = append(data, list(z))
      }
      names(data) = greeks
      total_data = append(total_data, list(data))
    }
    names(total_data) = dates
    return  (total_data)
  }
  all_data$btc = structure(calc_greeks("btc"), class = "btc")
  all_data$eth = structure(calc_greeks("eth"), class = "eth")
  
  all_dates =  reactive({
    if(input$coin == 'btc'){
      all_dates = all_data$btc[[match(input$settlement,names(all_data$btc))]][match(input$greek, greeks)][[1]]
    }
    else{
      all_dates = all_data$eth[[match(input$settlement,names(all_data$eth))]][match(input$greek, greeks)][[1]]
    }
      return(all_dates)
  })
     
  df <- reactive({
    return(rownames(all_dates()))
  })
  
  output$sliders <- renderUI({
    xv <- list(df())
    min_date = df()[1]
    max_date = df()[nrow(all_dates())]
    sliders <- lapply(1:length(xv), function(i) {
      inputName <- xv[i]
      sliderInput('n',
                  inputName,
                  min=as.Date(min_date,"%Y-%m-%d"),
                  max=as.Date(max_date,"%Y-%m-%d"),
                  value=as.Date(min_date,"%Y-%m-%d"),
                  step = length(xv))
    })
    do.call(tagList, sliders)
  })
  
  #output$selected_var <- renderText({ 
  #})
  
  output$plot1 <- renderPlot({
    plot(colnames(all_dates()),
         all_dates()[match(input$n,as.Date(rownames(all_dates())), "%Y-%m-%d"), ],
           ylab = input$greek, type = "b",
           xlab = "Price")
  })
 }