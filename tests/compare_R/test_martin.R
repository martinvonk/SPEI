context("spei")

data(wichita)
attach(wichita)
wichita$PET <- thornthwaite(wichita$TMED, 37.6475)
wichita$BAL <- wichita$PRCP - wichita$PET

data(balance)

data(cruts4)

x_vec <- as.numeric(wichita$BAL)
x_tsvec <- ts(x_vec, c(1980, 1), fr = 12)
spei1 <- SPEI::spei(x_tsvec, 1)$fitted
spei3 <- SPEI::spei(x_tsvec, 3)$fitted
write.csv(cbind("time" = time(x_tsvecs), "pexcess" = x_tsvec, "spei1" = spei1, "spei3" = spei3), "spei_r.csv")

# read_csv <- read.csv('C:/Users/.../E5L_8810_spei30D_19812021_logL_rect.csv')

# dataTable <- data.table(read_csv)

# bic_daily <- dataTable$ppn - dataTable$pev

# spei.cell <- spei(

#   ts(bic_daily, freq=365, start=c(1981,1,1)),

#   scale = 30,

#   kernel= list(type="rectangular", shift=0),

#   distribution="log-Logistic",

#   fit= "ub-pwm",

#   params=NULL,

#   na.rm=F,

#   ref.start=NULL,

#   ref.end=NULL

# )
