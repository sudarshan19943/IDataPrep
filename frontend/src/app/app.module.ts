import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';

import {BrowserAnimationsModule} from '@angular/platform-browser/animations';
 import {MatStepperModule} from '@angular/material/stepper';
 import {MatButtonModule} from '@angular/material/button';
 import {MatInputModule} from '@angular/material/input';
 import {MatChipsModule} from '@angular/material/chips';
 import {MatSelectModule} from '@angular/material/select';
 import {MatIconModule} from '@angular/material/icon';
 import {MatCheckboxModule} from '@angular/material/checkbox';


@NgModule({
  declarations: [
    AppComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    BrowserAnimationsModule,
    MatStepperModule,
    MatButtonModule,
    MatInputModule,
    MatChipsModule,
    MatSelectModule,
    MatIconModule,
    MatCheckboxModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
