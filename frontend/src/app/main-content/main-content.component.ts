import { Component, OnInit, ViewChild, AfterViewInit, ChangeDetectorRef } from '@angular/core';
import { firstSteps, typeCleanOnly, typeCleanAndClassify } from './Steps.js';
import { MatHorizontalStepper } from '@angular/material/stepper';

@Component({
  selector: 'app-main-content',
  templateUrl: './main-content.component.html',
  styleUrls: ['./main-content.component.scss']
})
export class MainContentComponent implements OnInit, AfterViewInit {
  firstSteps = firstSteps;
  otherSteps = typeCleanOnly;
  forClassification = true;
  @ViewChild('stepper', {static: true}) stepper: MatHorizontalStepper;

  constructor(private cdr: ChangeDetectorRef) { }

  ngOnInit() {
    if (this.forClassification) {
      this.otherSteps = typeCleanAndClassify;
    } else {
      this.otherSteps = typeCleanOnly;
    }
  }

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
    console.log('Marking Step ' + i + ' as Completed');
    this.stepper.selectedIndex = i;
    this.stepper.selected.completed = true;
    this.cdr.detectChanges();
  }

  forClassificationChange(event: any) {
    this.forClassification = event;
    if (this.forClassification) {
      this.otherSteps = typeCleanAndClassify;
    } else {
      this.otherSteps = typeCleanOnly;
    }
  }

  test() {
    console.log("Blah")
  }
}
