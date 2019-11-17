fluidPage(
  verticalLayout(
    titlePanel("Cryptocurrency Options Greek Analysis"),
    wellPanel(
      selectInput("coin", "Coin:", 
                  c("Bitcoin" = "btc",
                    "Ethereum" ="eth")
      ),
      selectInput("settlement", "Settlement Date:", 
                  names(all_data$btc)
      ),
      uiOutput("sliders"),
      selectInput("greek", "Greek:", 
                  c("Put Vega" = "p_vega",
                    "Put Delta" ="p_delta",
                    "Put Theta" ="p_theta",
                    "Put Gamma" ="p_gamma",
                    "Call Vega" ="c_vega",
                    "Call Delta" ="c_delta",
                    "Call Theta" ="c_theta",
                    "Call Gamma" ="c_gamma")
      )
    ),
    textOutput("selected_var"),
    plotOutput("plot1")
  )
)