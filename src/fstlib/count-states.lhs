> module Main where

> import Data.List (intercalate)
> import qualified Data.Set as Set
> import LTK

> main :: IO ()
> main = interact (f . summarize . from ATT)
>     where f (a, b, c) = unlines [intercalate "," $ map show [a,b,c]]

> summarize :: (Ord n, Ord e) => FSA n e -> (Int, Int, Int)
> summarize f = ( Set.size $ states f'
>               , Set.size $ states m
>               , Set.size $ jEquivalence m)
>     where f' = normalize f
>           m  = syntacticMonoid f'
