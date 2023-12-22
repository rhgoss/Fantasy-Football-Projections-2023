library(shiny)
library(tidyverse)
library(dplyr)
library(ggplot2)
library(rsconnect)
library(DBI)
library(odbc)
library(RPostgres)
library(nflplotR)
library(nflreadr)
library(ggthemes)
library(shinythemes)
library(gt)

con <- dbConnect(RPostgres::Postgres(), 
                 dbname = "postgres",
                 port = 5432,
                 user = "postgres",
                 password = rstudioapi::askForPassword("Database password"))

players <- load_players(file_type = getOption("nflreadr.prefer", default = "rds"))
projections <- dbGetQuery(con, "SELECT * FROM nfl_projections")
adp <- dbGetQuery(con, "SELECT * FROM nfl_adp")

adp_join <- adp %>% 
  mutate(player = str_remove_all(player, '\\.'))
projections_join <- projections %>% 
  mutate(player = str_remove_all(player, '\\.'))
players_join <- players %>% 
  mutate(display_name = str_remove_all(display_name, '\\.'))

 

summary <- adp_join %>% 
  left_join(projections_join,
             by = c('player' = 'player',
                    'team' = 'team',
                    'position' = 'position',
                    'date' = 'date'),
             relationship = 'many-to-many') %>%
  mutate(team = toupper(team)) %>% 
  left_join(players_join,
             by = c('player' = 'display_name',
                    'team' = 'team_abbr',
                    'position' = 'position'),
             relationship = 'many-to-many')
summary_photo <- summary %>% 
  distinct(gsis_id, .keep_all = TRUE)
 
ui <- fluidPage(
  navbarPage("Fantasy Football Drafting Dashboard",
     theme = shinytheme("yeti"),
     tabPanel(
       "Projections and ADP",
       sidebarLayout(
         sidebarPanel(
           helpText("This is using the most recent projections/adp data."),
           conditionalPanel(
             'input.dataset === "projections"',
             checkboxGroupInput("proj_vars", "Choose Which Columns to Show:",
                                names(projections), selected = c('player', 'team', 'position', 'espn_projections_l1', 'vegas_projections_l1'))
           ),
           conditionalPanel(
             'input.dataset === "adp"',
             checkboxGroupInput("adp_vars", "Choose Which Columns to Show:",
                                names(adp), selected = c('player', 'team', 'position', 'adp'))
           )
         ),
         mainPanel(
           tabsetPanel(
             id = 'dataset',
             tabPanel("projections", DT::dataTableOutput("table1")),
             tabPanel("adp", DT::dataTableOutput("table2")),
           )
         )
       )
     ),
     tabPanel(
       "Player Summaries",
       sidebarLayout(
         sidebarPanel(width = 4, 
                      helpText("Select a player to see their draft trends over time.")),
         mainPanel(
           tabPanel("summary", 
                    selectInput(
                      "player", "Select a player:",
                      choices = summary_photo$player
                    ),
                    fluidRow(
                      column(6,  plotOutput("headshot_plot")),
                      column(6,  plotOutput("adp_plot")),
                      column(6,  plotOutput("posrank_plot")),
                      column(6,  plotOutput("rank_plot"))
                    )
           )
         )
       )
     )
  )
)


server <- function(input, output) {
  
  # Filter data based on selections
  output$table1 <- DT::renderDataTable({
    recent_projections <- subset(projections, date == max(date))
    DT::datatable((recent_projections[, input$proj_vars]), rownames = FALSE)
  })
  
  output$table2 <- DT::renderDataTable({
    recent_adp <- subset(adp, date == max(date))
    DT::datatable((recent_adp[, input$adp_vars]), rownames = FALSE)
  })
  
  output$headshot_plot <- renderPlot({
    selected_player <- input$player
    selected_headshot <- summary_photo$gsis_id[summary_photo$player == selected_player]
    
    ggplot(summary_photo) +
      geom_nfl_headshots(aes(x = 0, y = 0, player_gsis = selected_headshot)) +
      theme(
        axis.title.x = element_blank(), 
        axis.title.y = element_blank(),
        axis.text.x = element_blank(),  
        axis.text.y = element_blank(),
        panel.grid.major = element_blank(),
        panel.grid.minor = element_blank(),
        axis.line = element_blank(),
        panel.border = element_blank(),
        axis.ticks = element_blank()
      )
  })
  
  output$adp_plot <- renderPlot({
    selected_player <- input$player
    adp_data <- subset(summary, player == selected_player, select = c('player', 'adp', 'date', 'overall rank', 'position rank'))
    
    ggplot(adp_data, aes(x = date, y = adp)) +
      geom_line(linetype= "dotdash", color = "gray") +
      geom_point(size = 2) +
      theme(
        plot.title = element_text(face = "bold", hjust = 0.5)
      ) +
      labs(
        x = "Date",
        y = "Average Draft Position",
        title = "Average Draft Position Over Time"
      ) +
      theme_igray()
  })
  
  output$posrank_plot <- renderPlot({
    selected_player <- input$player
    adp_data <- subset(summary, player == selected_player, select = c('player', 'adp', 'date', 'overall rank', 'position rank'))
    
    ggplot(adp_data, aes(x = date, y = `position rank`)) + 
      geom_line(linetype= "dotdash", color = "gray") +
      geom_point(size = 2) +
      theme(
        plot.title = element_text(face = "bold", hjust = 0.5)
      ) +
      labs(
        x = "Date",
        y = "Position Draft Rank",
        title = "Position Draft Rank Over Time"
      ) +
      theme_igray()
  })
  
  output$rank_plot <- renderPlot({
    
    selected_player <- input$player
    adp_data <- subset(summary, player == selected_player, select = c('player', 'adp', 'date', 'overall rank', 'position rank'))
    
    ggplot(adp_data, aes(x = date, y = `overall rank`, group = 1)) + 
      geom_line(linetype= "dotdash", color = "gray") +
      geom_point(size = 2) +
      theme(
        plot.title = element_text(face = "bold", hjust = 0.5)
      ) +
      labs(
        x = "Date",
        y = "Draft Rank",
        title = "Overall Draft Rank Over Time"
      ) +
      theme_igray()
  })
}

shinyApp(ui, server)
