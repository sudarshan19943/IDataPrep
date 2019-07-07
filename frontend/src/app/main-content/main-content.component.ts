import { Component, OnInit, ViewChild, AfterViewInit, ChangeDetectorRef } from '@angular/core';
import { typeCleanOnly, typeCleanAndClassify } from './Steps.js';
import { MatHorizontalStepper } from '@angular/material/stepper';

@Component({
  selector: 'app-main-content',
  templateUrl: './main-content.component.html',
  styleUrls: ['./main-content.component.scss']
})
export class MainContentComponent implements OnInit, AfterViewInit {
  steps = typeCleanOnly;
  forClassification = false;
  @ViewChild('stepper', {static: true}) stepper: MatHorizontalStepper;

  constructor(private cdr: ChangeDetectorRef) { }

  ngOnInit() {}

  ngAfterViewInit() {
    // dev purposes
      this.markStepCompleted(0);
      this.markStepCompleted(1);
      this.markStepCompleted(2);
      this.markStepCompleted(3);
      this.stepper.selectedIndex = 0;
      this.cdr.detectChanges();
  }

  markStepCompleted(i: number) {
    this.stepper.selectedIndex = i;
    this.stepper.selected.completed = true;
    this.cdr.detectChanges();
  }

  togglePurpose() {
    this.forClassification = !this.forClassification;
    if (this.forClassification) {
      this.steps = typeCleanAndClassify;
    } else {
      this.steps = typeCleanOnly;
    }
  }

}
