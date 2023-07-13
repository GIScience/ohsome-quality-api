# title: "Self-starting two-steps-sigmoidal function"
# author: "Josephine Brückner"

doubleSFun <- function(input, e, f, k, b, Z, c, ...) {
  e+(f-e)*1/2*(tanh(k*(input-b))+1)+(Z-f)*1/2*(tanh(k*(input-c))+1)
}

doubleS.init <- function(mCall, LHS, data, ...)
{    xy <- sortedXyData(mCall[["input"]], LHS, data)
x <-  xy[, "x"]; y <- xy[, "y"]

e <- min(y)
Z <- max(y)
f <- max(y)/2
b <- x[which.min(y)]
c <- max(x)*0.5
k <- 10
model <- "NA"
count <- 0

while(model[1]=="NA")
{ k <- k/10
count <- count + 1

model <- tryCatch(
  nls(y ~ doubleSFun(x, e, f, k, b, Z, c), start=c(e=min(y), f=max(y)/2, b=x[which.min(y)], Z=max(y), c=c, k=k), data),
  error = function(e) paste0("NA"))

if (count > 100)
{break}
}

start <- c(e, f, k, b, Z, c)
names(start) <- mCall[c("e", "f", "k", "b", "Z", "c")]
start
}


SSdoubleS <- selfStart(doubleSFun, doubleS.init, parameters=c("e", "f", "k", "b", "Z", "c"))
